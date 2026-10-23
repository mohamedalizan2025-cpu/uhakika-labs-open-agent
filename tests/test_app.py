"""HTTP tests for the FastAPI app: liveness + the judge-facing POST /run.

Runs the REAL sample-mode pipeline (fixture adapter) end-to-end over the ASGI app.
No network, no credentials, no ``.env``.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from agent.config import ENV_SAMPLE_MODE, Settings
from agent.main import create_app


def _sample_client() -> TestClient:
    settings = Settings.from_environ({ENV_SAMPLE_MODE: "true"})
    return TestClient(create_app(settings))


def test_create_app_exposes_health_and_run() -> None:
    app = create_app()
    paths = {route.path for route in app.routes}
    assert "/health" in paths
    assert "/run" in paths


def test_health_endpoint_returns_ok() -> None:
    client = _sample_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_run_hero_invoice_derives_grounded_conclusion() -> None:
    client = _sample_client()
    response = client.post(
        "/run",
        json={
            "question": "Why hasn't our TZS 126,000,000 invoice been paid?",
            "invoice_id": "INV-004",
            "sample_mode": True,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["revenue_at_risk"] == 126000000
    # The supported cause is derived from CMP-005 + CLAUSE-7.2 at runtime.
    assert body["supported_cause"] == "Required compliance / tax evidence missing"
    assert body["blocker_class"] == "execution_documentation"
    # H1-H3 are rejected with evidence-based reasons.
    rejected_ids = {item["id"] for item in body["rejected_hypotheses"]}
    assert rejected_ids == {"H1", "H2", "H3"}
    # Every claim traces to cited evidence IDs.
    cited = {ev["evidence_id"] for ev in body["evidence"]}
    assert {"CMP-005", "CLAUSE-7.2", "INV-004"} <= cited
    # Consequential action stays behind the human approval gate.
    assert body["approval_status"] == "pending"
    # Operational trace exists and never claims a model/provider in sample mode.
    assert isinstance(body["trace"], list) and body["trace"]
    assert all(entry.get("model_route") in (None, "null") for entry in body["trace"])


def test_run_unknown_invoice_is_insufficient_not_fabricated() -> None:
    client = _sample_client()
    response = client.post(
        "/run",
        json={
            "question": "Why is invoice XYZ unpaid?",
            "invoice_id": "INV-999",
            "sample_mode": True,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["supported_cause"] == "insufficient_evidence"
    assert body["revenue_at_risk"] == 0
    assert body["approval_status"] == "not_required"
