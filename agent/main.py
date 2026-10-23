"""Uhakika application entry point (FastAPI).

Wires the FastAPI app, loads environment-driven configuration, and exposes the
single judge-facing ``POST /run`` investigation endpoint (see ARCHITECTURE.md §10)
alongside ``GET /health``. ``POST /run`` runs the real sample-mode pipeline over
the credential-free fixture adapter and derives its conclusion at runtime.

``fastapi`` is installed in ``.venv`` from the pinned ``requirements.txt``
(AGENTS.md §8 dependency-authorization policy). Run locally with
``uvicorn agent.main:app --reload``.
"""
from __future__ import annotations

from fastapi import FastAPI

from agent.config import Settings
from agent.investigator_agent import InvestigatorAgent
from agent.models import RunRequest, RunResponse


def create_app(settings: Settings | None = None) -> FastAPI:
    """App factory. Loads env-driven settings and wires the judge-facing API."""
    settings = settings or Settings.from_environ()
    app = FastAPI(title="Uhakika", version="0.0.0-scaffold")
    app.state.settings = settings

    @app.get("/health")
    def health() -> dict[str, bool]:
        # Liveness marker only.
        return {"ok": True}

    @app.post("/run", response_model=RunResponse)
    def run(request: RunRequest) -> RunResponse:
        # The single judge-facing endpoint. In sample mode it runs the real
        # pipeline over the credential-free fixture adapter and derives the
        # conclusion at runtime (no stored answer).
        investigator = InvestigatorAgent(app.state.settings)
        return investigator.run(request)

    return app


app = create_app()
