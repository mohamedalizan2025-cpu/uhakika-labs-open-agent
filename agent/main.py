"""Uhakika application entry point (FastAPI).

Wires the FastAPI app, loads environment-driven configuration, and exposes the
judge-facing ``POST /run`` investigation endpoint and ``GET /health`` readiness
endpoint.

``POST /run`` honors the explicit ``sample_mode`` field from the request:
- ``sample_mode=true`` runs the credential-free sample pipeline.
- ``sample_mode=false`` requires a live configuration; if live integrations are
  not ready, the endpoint returns a clear 503 (NAMES only), never falling back
  silently.

``GET /health`` returns sanitized operational readiness (no secrets, no URLs
with credentials).

Run locally with ``uvicorn agent.main:app --reload``.
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException

from agent.config import Settings
from agent.investigator_agent import InvestigatorAgent
from agent.models import RunRequest, RunResponse


def _sample_ready(settings: Settings) -> bool:
    """Sample mode is always available (credential-free, fixtures on disk)."""
    return True


def _live_ready(settings: Settings) -> bool:
    """Live mode requires all six canonical variables populated AND validated."""
    return len(settings.missing_for_live()) == 0


def create_app(settings: Settings | None = None) -> FastAPI:
    """App factory. Loads env-driven settings and wires the judge-facing API."""
    settings = settings or Settings.from_environ()
    app = FastAPI(title="Uhakika", version="0.0.0")
    app.state.settings = settings

    @app.get("/health")
    def health() -> dict:
        """Sanitized operational readiness — no secrets, no URLs with credentials."""
        missing = settings.missing_for_live()
        return {
            "ok": True,
            "default_mode": "sample" if settings.sample_mode else "live",
            "sample_ready": _sample_ready(settings),
            "live_ready": _live_ready(settings),
            "integrations": {
                "zetaris": {
                    "status": "sample_only" if not _live_ready(settings) else "live_ready",
                    "missing": [n for n in missing if n.startswith("ZETARIS_")],
                },
                "nightshift": {
                    "status": "not_configured" if any(n.startswith("METERLESS_") for n in missing) else "live_ready",
                    "missing": [n for n in missing if n.startswith("METERLESS_")],
                },
            },
            "missing_env_names": list(missing),
        }

    @app.post("/run", response_model=RunResponse)
    def run(request: RunRequest) -> RunResponse:
        """Single judge-facing investigation endpoint.

        Honors the explicit request.sample_mode: sample=true always works;
        sample=false requires live readiness or returns 503 (names only).
        """
        if not request.sample_mode:
            # Live requested — verify readiness before proceeding.
            missing = settings.missing_for_live()
            if missing:
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "live_mode_not_ready",
                        "message": "Live mode requires environment variables that are not configured.",
                        "missing_env_names": missing,
                    },
                )
        # Build the investigator with the requested mode.
        # Sample mode uses the credential-free fixture adapter.
        # Live mode would use the validated Zetaris + Nightshift adapters.
        from dataclasses import replace
        effective_settings = replace(settings, sample_mode=request.sample_mode)
        investigator = InvestigatorAgent(effective_settings)
        return investigator.run(request)

    return app


app = create_app()
