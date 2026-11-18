"""
PulseGuard Core Microservice
----------------------------
This application serves as the workload monitored by the PulseGuard self-healing engine.

DevOps Architecture Role:
In modern automated deployment systems (Docker, Kubernetes, AWS ECS, custom deployment scripts),
the deployment orchestrator does not assume an application is working just because the process started.
Instead, it repeatedly polls an automated health endpoint (/health).

Health Check Flow:
1. deploy.sh boots up the new container version.
2. deploy.sh sends periodic HTTP GET requests to /health.
3. If /health returns HTTP 200 within a timeout threshold, the release is declared SUCCESSFUL.
4. If /health returns HTTP 500 (or fails to respond), the release is declared FAILED,
   and the deployment engine automatically triggers rollback.sh.
"""

import os
from fastapi import FastAPI, Response, status
from pydantic import BaseModel

app = FastAPI(
    title="PulseGuard",
    version="1.0.0",
    description="Workload microservice with automated health-check and failure simulation for self-healing deployment pipelines.",
)

# In-memory runtime state for chaos / failure simulation (can also be preset via ENV)
# This allows testing the automated rollback mechanism safely without editing code.
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
        "version": "1.0.0",
        "status": "online",
        "docs_url": "/docs",
        "health_url": "/health",
    }


@app.get("/health", tags=["Observability"])
def health_check(response: Response):
    """
    Health Check Endpoint (DevOps Liveness & Readiness Probe):
    
    Returns:
    - HTTP 200 OK: Service is healthy; deployment engine promotes the release.
    - HTTP 500 Internal Server Error: Simulated failure or database crash;
      deployment engine catches this status and triggers an automated rollback.
    """
    if runtime_state["simulate_failure"]:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status": "degraded",
            "service": "pulseguard",
            "version": "1.0.0",
            "error": "Simulated deployment failure triggered for self-healing verification.",
        }

    response.status_code = status.HTTP_200_OK
    return {
        "status": "healthy",
        "service": "pulseguard",
        "version": "1.0.0",
    }


@app.post("/api/v1/simulate-failure", tags=["DevOps Chaos Engineering"])
def set_failure_simulation(payload: FailureSimulationRequest):
    """
    Chaos Engineering Hook:
    Enables or disables simulated application failure at runtime.
    Used during Milestone 6 to demonstrate PulseGuard's automatic detection and self-healing rollback.
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
