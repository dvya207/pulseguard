"""
PulseGuard Infrastructure Monitoring Tests
-------------------------------------------
Validates the /api/v1/monitoring endpoint that returns
real infrastructure metrics from Prometheus including
CPU, memory, disk, and container resource usage.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_prometheus_response():
    """Mock Prometheus API response structure."""
    def _mock_response(value):
        return {
            "status": "success",
            "data": {
                "result": [
                    {
                        "metric": {},
                        "value": [1234567890, str(value)]
                    }
                ]
            }
        }
    return _mock_response


def test_monitoring_endpoint_success(mock_prometheus_response):
    """Test that the monitoring endpoint returns expected metrics structure."""
    with patch('app.main.urlopen') as mock_urlopen:
        # Mock successful Prometheus responses
        mock_response = MagicMock()
        mock_response.read.return_value = str(mock_prometheus_response(42.5)).replace("'", '"').encode()
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_urlopen.return_value = mock_response
        
        response = client.get("/api/v1/monitoring")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["success", "partial"]
        assert "metrics" in data


def test_monitoring_endpoint_structure():
    """Test that monitoring endpoint has correct structure even on errors."""
    response = client.get("/api/v1/monitoring")
    
    # Should either succeed or return 503
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "metrics" in data
        assert "status" in data
        
        # Check for expected metric keys
        metrics = data["metrics"]
        expected_keys = [
            "application_up",
            "cpu_usage_percent",
            "memory_used_bytes",
            "memory_total_bytes",
            "memory_used_percent",
            "disk_used_bytes",
            "disk_total_bytes",
            "disk_used_percent",
        ]
        
        # All expected keys should be present (even if None)
        for key in expected_keys:
            assert key in metrics


def test_monitoring_endpoint_timeout():
    """Test that monitoring endpoint handles Prometheus timeout gracefully."""
    with patch('app.main.urlopen', side_effect=TimeoutError("Connection timeout")):
        response = client.get("/api/v1/monitoring")
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
        assert "Prometheus" in data["detail"]


def test_monitoring_metrics_types():
    """Test that returned metrics have appropriate types when available."""
    response = client.get("/api/v1/monitoring")
    
    if response.status_code == 200:
        data = response.json()
        metrics = data["metrics"]
        
        # Check numeric metrics are either None or numeric
        numeric_metrics = [
            "cpu_usage_percent",
            "memory_used_percent",
            "disk_used_percent",
        ]
        
        for key in numeric_metrics:
            if key in metrics and metrics[key] is not None:
                assert isinstance(metrics[key], (int, float)), f"{key} should be numeric"
        
        # Check container metrics are lists when present
        if "container_cpu_usage" in metrics and metrics["container_cpu_usage"] is not None:
            assert isinstance(metrics["container_cpu_usage"], list)
