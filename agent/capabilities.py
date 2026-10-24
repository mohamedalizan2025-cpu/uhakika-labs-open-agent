"""Runtime integration capability tracking (Phase 6A).

Tracks whether each external integration is *configured*, *reachable*,
*verified*, and *operational*. This is NOT a persisted global — it is
instantiated per application lifespan and can be probed, tested, and
injected. No credential values are ever stored or logged here; only
environment-variable NAMES and boolean capability flags.

Definitions:
- configured: required environment-variable values are present (not None/empty).
- reachable: the service answered a safe connectivity check (e.g. GET /health).
- verified: a real protocol request (not just connectivity) succeeded.
- operational: the integration has an implemented executable adapter AND
  its verification passed.

`live_ready` (global) is True only when ALL required integrations are operational.
Currently (Phase 6A), NO integration is operational, so live_ready is always False.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from agent.config import (
    Settings,
    ENV_METERLESS_BASE_URL,
    ENV_METERLESS_RUNTIME_TOKEN,
    ENV_METERLESS_MODEL,
    ENV_ZETARIS_REST_URL,
    ENV_ZETARIS_ORG_ID,
    ENV_ZETARIS_API_KEY,
)


@dataclass
class IntegrationCapability:
    """Sanitized per-integration state; never stores credential values."""

    configured: bool = False
    reachable: bool = False
    verified: bool = False
    operational: bool = False
    missing_env_names: list[str] = field(default_factory=list)


@dataclass
class CapabilityRegistry:
    """Aggregates integration capabilities; controls the `live_ready` gate.

    Instantiate once in `create_app()` and inject or probe. For testability,
    all fields start False; nothing is auto-set merely by variables existing.
    """

    zetaris: IntegrationCapability = field(default_factory=IntegrationCapability)
    nightshift: IntegrationCapability = field(default_factory=IntegrationCapability)
    scout_intent_verified: bool = False
    scout_intent_status: str = "fallback"

    def update_configuration(self, settings: Settings) -> None:
        """Update the `configured` flag based on which env vars are present.

        This does NOT set reachable/verified/operational — those require
        actual probes that only a running live adapter can perform.
        """
        # Zetaris: check canonical variables
        zetaris_vars = {
            ENV_ZETARIS_REST_URL: settings.zetaris_rest_url,
            ENV_ZETARIS_ORG_ID: settings.zetaris_org_id,
            ENV_ZETARIS_API_KEY: settings.zetaris_api_key,
        }
        self.zetaris.missing_env_names = [n for n, v in zetaris_vars.items() if not v]
        self.zetaris.configured = len(self.zetaris.missing_env_names) == 0

        # Nightshift: check canonical variables
        ns_vars = {
            ENV_METERLESS_BASE_URL: settings.meterless_base_url,
            ENV_METERLESS_RUNTIME_TOKEN: settings.meterless_runtime_token,
            ENV_METERLESS_MODEL: settings.meterless_model,
        }
        self.nightshift.missing_env_names = [n for n, v in ns_vars.items() if not v]
        self.nightshift.configured = len(self.nightshift.missing_env_names) == 0

    @property
    def live_ready(self) -> bool:
        """True only when ALL required live integrations are operational."""
        return (
            self.zetaris.operational
            and self.nightshift.operational
            and self.scout_intent_verified
        )

    def health_payload(self) -> dict:
        """Sanitized /health integrations section — no values, only names/flags."""
        return {
            "zetaris": {
                "configured": self.zetaris.configured,
                "reachable": self.zetaris.reachable,
                "verified": self.zetaris.verified,
                "operational": self.zetaris.operational,
                "missing_env_names": list(self.zetaris.missing_env_names),
            },
            "nightshift": {
                "configured": self.nightshift.configured,
                "reachable": self.nightshift.reachable,
                "verified": self.nightshift.verified,
                "operational": self.nightshift.operational,
                "missing_env_names": list(self.nightshift.missing_env_names),
            },
            "scout_intent": {
                "status": self.scout_intent_status,
                "verified": self.scout_intent_verified,
            },
        }
