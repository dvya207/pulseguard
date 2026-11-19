"""
PulseGuard Core Microservice
----------------------------
This application serves as the workload monitored by the PulseGuard self-healing engine
and observability platform.

DevOps Architecture Role:
1. Health Probing (/health):
   Used by deployment scripts and orchestrators to evaluate liveness/readiness.
2. Metrics Exposition (/metrics/):
   Scraped by Prometheus every 15s to monitor request throughput, error rates,
   latency distribution, and container resource consumption.
3. Chaos / Failure Simulation (/api/v1/simulate-failure):
   Enables controlled failure injection to validate self-healing rollback behavior.
"""

import os
import time
from fastapi import FastAPI, Request, Response, status
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, make_asgi_app
from starlette.routing import Match
from . import __version__
from .self_heal_metrics import register_self_heal_metrics
register_self_heal_metrics()

APP_VERSION = os.getenv("PULSEGUARD_VERSION", __version__)

app = FastAPI(
    title="PulseGuard",
    version=APP_VERSION,
    description="Workload microservice with automated health-check, metrics, and failure simulation.",
)

# -----------------------------------------------------------------------------
# Prometheus Metrics Instrumentation
# -----------------------------------------------------------------------------
# Request counter with low-cardinality labels (method, route template, HTTP status)
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total count of HTTP requests processed by PulseGuard",
    ["method", "route", "status"],
)

# Request latency histogram with standard web service latency buckets
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "Histogram of HTTP request durations in seconds",
    ["method", "route", "status"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0),
)

# Mount the Prometheus ASGI application directly onto /metrics.
# Default registry retains standard Python process metrics (process_cpu_seconds_total,
# process_resident_memory_bytes, python_info, etc.) automatically.
app.mount("/metrics", make_asgi_app())


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """
    HTTP middleware for tracking application metrics.
    - Captures request duration and status code.
    - Resolves normalized route paths (e.g. /health) to prevent metric label cardinality explosion.
    - Excludes internal /metrics scrapes to prevent scraping activity from polluting telemetry.
    """
    path = request.url.path

    # Exclude metrics scrapes from application metrics
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

        # Resolve normalized route template rather than raw dynamic path
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
# Runtime State & Existing Endpoints
# -----------------------------------------------------------------------------
runtime_state = {
    "simulate_failure": os.getenv("SIMULATE_FAILURE", "false").lower() in ("true", "1", "yes")
}


class FailureSimulationRequest(BaseModel):
    enabled: bool


@app.get("/", tags=["General"])
def read_root():
    """
    Root endpoint providing basic service metadata and links to key tools.
    """
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
    Health Check Endpoint (DevOps Liveness & Readiness Probe):
    
    Returns:
    - HTTP 200 OK: Service is healthy; deployment engine promotes the release.
    - HTTP 500 Internal Server Error: Simulated failure or crash;
      deployment engine catches this status and triggers an automated rollback.
    """
    if runtime_state["simulate_failure"]:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status": "degraded",
            "service": "pulseguard",
            "version": APP_VERSION,
            "error": "Simulated deployment failure triggered for self-healing verification.",
        }

    response.status_code = status.HTTP_200_OK
    return {
        "status": "healthy",
        "service": "pulseguard",
        "version": APP_VERSION,
    }


@app.post("/api/v1/simulate-failure", tags=["DevOps Chaos Engineering"])
def set_failure_simulation(payload: FailureSimulationRequest):
    """
    Chaos Engineering Hook:
    Enables or disables simulated application failure at runtime.
    Used to demonstrate PulseGuard's automatic detection and self-healing rollback.
    """
    runtime_state["simulate_failure"] = payload.enabled
    return {
        "simulate_failure": runtime_state["simulate_failure"],
        "message": (
            "Failure simulation ACTIVE. /health will now return HTTP 500."
            if payload.enabled
            else "Failure simulation DEACTIVATED. /health will now return HTTP 200."
        ),
    }
