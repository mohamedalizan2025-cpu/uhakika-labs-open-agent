"""Import test for the FastAPI app skeleton (pytest).

FastAPI is installed in ``.venv`` from the pinned ``requirements.txt``, so this
module imports it directly. It verifies the app factory returns a FastAPI
instance, exposes only the liveness route, and that ``GET /health`` returns the
liveness payload — with no investigation endpoint yet.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from agent.main import create_app


def test_create_app_exposes_health_but_no_run() -> None:
    app = create_app()
    paths = {route.path for route in app.routes}
    assert "/health" in paths
    # Investigation endpoint must NOT exist yet (added in a later phase).
    assert "/run" not in paths


def test_health_endpoint_returns_ok() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}
