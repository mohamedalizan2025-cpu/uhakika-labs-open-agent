"""Uhakika application entry point (FastAPI SKELETON only).

Wires a minimal FastAPI app and loads configuration from the environment. It
deliberately contains NO investigation logic: the judge-facing ``POST /run``
investigation endpoint (see ARCHITECTURE.md §10) is added only in a later
approved phase.

``fastapi`` is installed in ``.venv`` from the pinned ``requirements.txt``
(AGENTS.md §8 dependency-authorization policy). Run locally with
``uvicorn agent.main:app --reload``.
"""
from __future__ import annotations

from fastapi import FastAPI

from agent.config import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """App factory. Loads env-driven settings; adds no investigation routes."""
    settings = settings or Settings.from_environ()
    app = FastAPI(title="Uhakika", version="0.0.0-scaffold")
    app.state.settings = settings

    @app.get("/health")
    def health() -> dict[str, bool]:
        # Liveness marker only. Not an investigation endpoint.
        return {"ok": True}

    return app


app = create_app()
