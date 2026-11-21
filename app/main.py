
"""
PulseGuard Core Microservice
----------------------------
FastAPI workload monitored by the PulseGuard self-healing engine
and observability platform.
"""

import os
import time
import json
from urllib.parse import urlencode
from urllib.request import urlopen

from fastapi import FastAPI, Request, Response, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from prometheus_client import Counter, Gauge, Histogram, make_asgi_app
from starlette.routing import Match

from . import __version__
from .self_heal_metrics import register_self_heal_metrics

register_self_heal_metrics()

APP_VERSION = os.getenv("PULSEGUARD_VERSION", __version__)

PROMETHEUS_URL = os.getenv(
    "PROMETHEUS_URL",
    "http://prometheus:9090"
)

app = FastAPI(
    title="PulseGuard",
    version=APP_VERSION,
    description="Workload microservice with automated health-check, metrics, and failure simulation.",
)

# -----------------------------------------------------------------------------
# CORS Configuration - React Frontend
# -----------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Prometheus Metrics Instrumentation
# -----------------------------------------------------------------------------

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total count of HTTP requests processed by PulseGuard",
    ["method", "route", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "Histogram of HTTP request durations in seconds",
    ["method", "route", "status"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0),
)

APPLICATION_HEALTH = Gauge(
    "pulseguard_health",
    "Whether the PulseGuard health check is passing",
)

# Prometheus metrics endpoint
app.mount("/metrics", make_asgi_app())


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """
    Tracks HTTP request count and latency.
    Excludes internal Prometheus scrapes.
    """
    path = request.url.path

    if path.startswith("/metrics"):
        return await call_next(request)

    start_time = time.perf_counter()
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response

    except Exception:
        status_code = 500
        raise

    finally:
        duration = time.perf_counter() - start_time

        route_template = "unmatched"
        route_obj = request.scope.get("route")

        if route_obj and hasattr(route_obj, "path"):
            route_template = route_obj.path
        else:
            for route in request.app.routes:
                match, _ = route.matches(request.scope)
                if match == Match.FULL:
                    route_template = getattr(route, "path", "unmatched")
                    break

        method = request.method
        status_str = str(status_code)

        HTTP_REQUESTS_TOTAL.labels(
            method=method,
            route=route_template,
            status=status_str,
        ).inc()

        HTTP_REQUEST_DURATION_SECONDS.labels(
            method=method,
            route=route_template,
            status=status_str,
        ).observe(duration)


# -----------------------------------------------------------------------------
# Runtime State
# -----------------------------------------------------------------------------

runtime_state = {
    "simulate_failure": os.getenv(
        "SIMULATE_FAILURE", "false"
    ).lower() in ("true", "1", "yes")
}
APPLICATION_HEALTH.set(0 if runtime_state["simulate_failure"] else 1)


class FailureSimulationRequest(BaseModel):
    enabled: bool


# -----------------------------------------------------------------------------
# API Endpoints
# -----------------------------------------------------------------------------

@app.get("/", tags=["General"])
def read_root():
    """Provides basic service metadata."""
    return {
        "service": "PulseGuard",
        "version": APP_VERSION,
        "status": "online",
        "docs_url": "/docs",
        "health_url": "/health",
        "metrics_url": "/metrics/",
    }


@app.get("/health", tags=["Observability"])
def health_check(response: Response):
    """
    Health check endpoint.
    Returns HTTP 200 when healthy and HTTP 500 during simulated failure.
    """
    if runtime_state["simulate_failure"]:
        APPLICATION_HEALTH.set(0)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        return {
            "status": "degraded",
            "service": "pulseguard",
            "version": APP_VERSION,
            "error": "Simulated deployment failure triggered for self-healing verification.",
        }

    APPLICATION_HEALTH.set(1)
    response.status_code = status.HTTP_200_OK

    return {
        "status": "healthy",
        "service": "pulseguard",
        "version": APP_VERSION,
    }


@app.post("/api/v1/simulate-failure", tags=["DevOps Chaos Engineering"])
def set_failure_simulation(payload: FailureSimulationRequest):
    """
    Enables or disables simulated application failure.
    Used to verify automatic detection and rollback.
    """
    runtime_state["simulate_failure"] = payload.enabled
    APPLICATION_HEALTH.set(0 if payload.enabled else 1)

    return {
        "simulate_failure": runtime_state["simulate_failure"],
        "message": (
            "Failure simulation ACTIVE. /health will now return HTTP 500."
            if payload.enabled
            else "Failure simulation DEACTIVATED. /health will now return HTTP 200."
        ),
    }


# -----------------------------------------------------------------------------
# Live Prometheus Monitoring API
# -----------------------------------------------------------------------------

@app.get("/api/v1/monitoring", tags=["Monitoring"])
def get_monitoring_metrics():
    """
    Fetches live self-healing and infrastructure metrics from Prometheus.
    Returns CPU, memory, disk, and container resource metrics.
    """

    # Prometheus queries for infrastructure monitoring
    queries = {
        # Self-healing metrics (existing)
        "application_up": "pulseguard_health",
        "failures_detected": "self_heal_failures_detected_total",
        "recovery_attempts": "self_heal_recovery_attempts_total",
        "successful_recoveries": "self_heal_success_total",
        "failed_recoveries": "self_heal_failure_total",
        "rollbacks": "self_heal_rollback_total",
        
        # CPU metrics
        "cpu_usage_percent": '100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)',
        "load_average_1m": 'node_load1',
        
        # Memory metrics
        "memory_used_bytes": 'node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes',
        "memory_total_bytes": 'node_memory_MemTotal_bytes',
        "memory_used_percent": '((node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes) * 100',
        
        # Disk metrics
        "disk_used_bytes": 'node_filesystem_size_bytes{mountpoint="/"} - node_filesystem_avail_bytes{mountpoint="/"}',
        "disk_total_bytes": 'node_filesystem_size_bytes{mountpoint="/"}',
        "disk_used_percent": '((node_filesystem_size_bytes{mountpoint="/"} - node_filesystem_avail_bytes{mountpoint="/"}) / node_filesystem_size_bytes{mountpoint="/"}) * 100',
        "disk_read_bytes": 'rate(node_disk_read_bytes_total[5m])',
        "disk_write_bytes": 'rate(node_disk_written_bytes_total[5m])',
        
        # Container metrics (via cAdvisor)
        "container_cpu_usage": 'sum(rate(container_cpu_usage_seconds_total{id=~"/docker/.*"}[5m])) by (name)',
        "container_memory_usage": 'container_memory_usage_bytes{id=~"/docker/.*"}',
        "container_memory_limit": 'container_spec_memory_limit_bytes{id=~"/docker/.*"}',
        "container_status_running": 'container_start_time_seconds{id=~"/docker/.*"}',
    }

    metrics = {}
    errors = []

    try:
        for name, query in queries.items():
            params = urlencode({"query": query})
            url = f"{PROMETHEUS_URL}/api/v1/query?{params}"

            with urlopen(url, timeout=5) as response:
                result = json.loads(response.read())

            if result.get("status") != "success":
                errors.append(f"Prometheus query failed: {name}")
                continue

            values = result["data"]["result"]

            if values:
                # Handle instant queries with single result
                if name in ["cpu_usage_percent", "load_average_1m", "memory_used_percent", "disk_used_percent"]:
                    # These return multiple instances, take average
                    try:
                        metrics[name] = float(values[0]["value"][1])
                    except (IndexError, ValueError, TypeError):
                        metrics[name] = None
                elif name.startswith("container_"):
                    # Container metrics are lists
                    container_values = []
                    for item in values:
                        try:
                            container_values.append({
                                "metric": item.get("metric", {}).get("name")
                                or item.get("metric", {}).get("id", "unknown"),
                                "value": float(item["value"][1]),
                            })
                        except (KeyError, IndexError, TypeError, ValueError):
                            continue
                    metrics[name] = container_values
                else:
                    try:
                        metrics[name] = float(values[0]["value"][1])
                    except (IndexError, ValueError, TypeError):
                        metrics[name] = None
            else:
                if name.startswith("container_"):
                    metrics[name] = []
                else:
                    metrics[name] = None

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Unable to retrieve metrics from Prometheus: {str(exc)}"
        )

    return {
        "status": "success" if not errors else "partial",
        "version": APP_VERSION,
        "metrics": metrics,
        "errors": errors if errors else None
    }
