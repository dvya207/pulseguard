"""
PulseGuard Automated Test Suite
-------------------------------
DevOps Purpose:
These tests run in the CI/CD pipeline before any Docker image is built.
Validates service metadata, health probes, failure simulation hooks,
and Prometheus observability metrics exposition.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app, runtime_state

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_runtime_state():
    """Ensure every test starts with failure simulation turned OFF."""
    runtime_state["simulate_failure"] = False
    yield
    runtime_state["simulate_failure"] = False


def test_root_endpoint():
    """Verify that the root endpoint responds with HTTP 200 and valid metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "PulseGuard"
    assert data["status"] == "online"
    assert "version" in data
    assert "metrics_url" in data


def test_health_check_healthy():
    """Verify that under normal operation, /health returns HTTP 200 and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "pulseguard"
    assert data["version"] == "1.0.0"


def test_health_check_failure_simulation():
    """
    Verify the chaos/failure simulation hook:
    When simulate_failure is enabled, /health MUST return HTTP 500.
    """
    # 1. Enable failure simulation via the chaos hook
    toggle_res = client.post("/api/v1/simulate-failure", json={"enabled": True})
    assert toggle_res.status_code == 200
    assert toggle_res.json()["simulate_failure"] is True

    # 2. Check /health - must return HTTP 500 (degraded)
    health_res = client.get("/health")
    assert health_res.status_code == 500
    data = health_res.json()
    assert data["status"] == "degraded"
    metrics_res = client.get("/metrics/")
    assert "pulseguard_health 0.0" in metrics_res.text

    # 3. Disable failure simulation and verify recovery back to HTTP 200
    recover_res = client.post("/api/v1/simulate-failure", json={"enabled": False})
    assert recover_res.status_code == 200
    recovered_health = client.get("/health")
    assert recovered_health.status_code == 200
    assert recovered_health.json()["status"] == "healthy"
    assert "pulseguard_health 1.0" in client.get("/metrics/").text


def test_metrics_endpoint():
    """
    Verify that /metrics/ endpoint:
    - Responds with HTTP 200.
    - Exports custom application metrics (http_requests_total, http_request_duration_seconds).
    - Retains default Python process metrics (process_cpu_seconds_total, process_resident_memory_bytes).
    """
    # Trigger a request so application metrics are generated
    client.get("/health")

    # Fetch metrics
    metrics_res = client.get("/metrics/")
    assert metrics_res.status_code == 200
    output = metrics_res.text

    # Custom application metrics
    assert "http_requests_total" in output
    assert "http_request_duration_seconds" in output
    assert 'route="/health"' in output

    # Default Python process metrics
    assert "process_cpu_seconds_total" in output
    assert "process_resident_memory_bytes" in output
