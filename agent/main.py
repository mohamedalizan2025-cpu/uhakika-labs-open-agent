"""Uhakika application entry point (FastAPI).

Wires the FastAPI app, loads environment-driven configuration, and exposes the
judge-facing ``POST /run`` investigation endpoint and ``GET /health`` readiness
endpoint.

``POST /run`` honors the explicit ``sample_mode`` field from the request:
- ``sample_mode=true`` runs the credential-free sample pipeline.
- ``sample_mode=false`` requires ALL live integrations to be operational;
  otherwise returns a clear 503 (NAMES only), never falling back silently.

``GET /health`` returns sanitized operational readiness via the CapabilityRegistry.
No secrets, no URLs with credentials, no values — only names and boolean flags.

Run locally with ``uvicorn agent.main:app --reload``.
"""
from __future__ import annotations

from dataclasses import replace

from fastapi import FastAPI, HTTPException

from agent.capabilities import CapabilityRegistry
from agent.config import Settings
from agent.investigator_agent import InvestigatorAgent
from agent.models import RunRequest, RunResponse


def create_app(
    settings: Settings | None = None,
    capabilities: CapabilityRegistry | None = None,
) -> FastAPI:
    """App factory. Loads env-driven settings and wires the judge-facing API."""
    settings = settings or Settings.from_environ()

    # Build the capability registry; update 'configured' from settings.
    caps = capabilities or CapabilityRegistry()
    caps.update_configuration(settings)

    app = FastAPI(title="Uhakika", version="0.0.0")
    app.state.settings = settings
    app.state.capabilities = caps

    @app.get("/health")
    def health() -> dict:
        """Sanitized operational readiness — no secrets, no URLs with credentials."""
        all_missing = settings.missing_for_live()
        return {
            "ok": True,
            "default_mode": "sample" if settings.sample_mode else "live",
            "sample_ready": True,  # fixtures on disk, always available
            "live_ready": caps.live_ready,  # requires ALL operational
            "integrations": caps.health_payload(),
            "missing_env_names": list(all_missing),
        }

    @app.post("/run", response_model=RunResponse)
    def run(request: RunRequest) -> RunResponse:
        """Single judge-facing investigation endpoint.

        Honors the explicit request.sample_mode:
        - sample_mode=true always works (credential-free pipeline).
        - sample_mode=false requires live_ready; returns 503 if not operational.
        """
        if not request.sample_mode:
            # Live requested — verify FULL operational readiness.
            if not caps.live_ready:
                missing = settings.missing_for_live()
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "live_mode_not_operational",
                        "message": (
                            "Live mode requires all integrations to be operational "
                            "(configured, reachable, verified, adapter implemented). "
                            "Current state does not meet this threshold."
                        ),
                        "missing_env_names": missing if missing else [],
                        "live_ready": False,
                    },
                )
        # Build the investigator with the requested mode.
        effective_settings = replace(settings, sample_mode=request.sample_mode)
        investigator = InvestigatorAgent(effective_settings)
        return investigator.run(request)

    return app


app = create_app()
