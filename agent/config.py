"""Central configuration for Uhakika.

Reads ONLY the canonical environment-variable names defined in AGENTS.md §3 /
BUILD_PLAN.md §3. At module-import time the runtime calls `load_dotenv(override=False)`
to populate os.environ from a local, Git-ignored `.env` file (the owner's startup
convenience); existing OS-environment variables always take precedence.

Security model:
- The APPLICATION may load .env via python-dotenv (a standard library).
- An AI/operator MUST NEVER open, read, print, parse, or expose .env contents.
- Values loaded from .env are never logged or included in error messages.
- Secrets are masked in every repr/status/error; only variable NAMES appear.

Contract:
- The eight canonical variables are the only supported names.
- The prohibited legacy aliases (METERLESS_API_KEY, NEMOTRON_MODEL,
  ZETARIS_BASE_URL) are IGNORED — never read, never silently migrated.
- Missing values become ``None`` / a safe default; live-mode validation fails
  loudly and reports only the missing variable NAMES (never any value).
- No hardcoded endpoint, model ID, token, or API key lives in this module.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Mapping, Optional

from dotenv import load_dotenv

# Populate os.environ from the local .env (if present). override=False ensures
# that real environment variables always take precedence. This is a runtime
# convenience; the AI/operator never opens or inspects .env.
load_dotenv(override=False)

# --- Canonical environment-variable NAMES (values are never recorded here). ---
ENV_METERLESS_BASE_URL = "METERLESS_BASE_URL"
ENV_METERLESS_RUNTIME_TOKEN = "METERLESS_RUNTIME_TOKEN"  # secret
ENV_METERLESS_MODEL = "METERLESS_MODEL"
ENV_ZETARIS_REST_URL = "ZETARIS_REST_URL"
ENV_ZETARIS_ORG_ID = "ZETARIS_ORG_ID"
ENV_ZETARIS_API_KEY = "ZETARIS_API_KEY"  # secret
ENV_SAMPLE_MODE = "SAMPLE_MODE"
ENV_MAX_EVIDENCE_RETRIES = "MAX_EVIDENCE_RETRIES"

CANONICAL_ENV_NAMES: tuple[str, ...] = (
    ENV_METERLESS_BASE_URL,
    ENV_METERLESS_RUNTIME_TOKEN,
    ENV_METERLESS_MODEL,
    ENV_ZETARIS_REST_URL,
    ENV_ZETARIS_ORG_ID,
    ENV_ZETARIS_API_KEY,
    ENV_SAMPLE_MODE,
    ENV_MAX_EVIDENCE_RETRIES,
)

# Prohibited legacy aliases. Present in the environment but NEVER read/migrated.
LEGACY_ENV_NAMES: frozenset[str] = frozenset(
    {"METERLESS_API_KEY", "NEMOTRON_MODEL", "ZETARIS_BASE_URL"}
)

# Canonical names that carry secret material (masked everywhere).
SECRET_ENV_NAMES: frozenset[str] = frozenset(
    {ENV_METERLESS_RUNTIME_TOKEN, ENV_ZETARIS_API_KEY}
)

# Canonical variables required to run in LIVE mode.
LIVE_REQUIRED_ENV_NAMES: tuple[str, ...] = (
    ENV_METERLESS_BASE_URL,
    ENV_METERLESS_RUNTIME_TOKEN,
    ENV_METERLESS_MODEL,
    ENV_ZETARIS_REST_URL,
    ENV_ZETARIS_ORG_ID,
    ENV_ZETARIS_API_KEY,
)

_TRUTHY = {"1", "true", "yes", "on"}
# Non-secret operational default (not an endpoint/credential/model id).
DEFAULT_MAX_EVIDENCE_RETRIES = 3


class ConfigError(Exception):
    """Raised when configuration is invalid for the requested mode.

    The message contains only environment-variable NAMES, never values.
    """


def _presence(value: Optional[str]) -> str:
    return "set" if value else "unset"


def _parse_bool(value: Optional[str]) -> bool:
    return (value or "").strip().lower() in _TRUTHY


def _parse_retries(value: Optional[str]) -> int:
    if value is None or value.strip() == "":
        return DEFAULT_MAX_EVIDENCE_RETRIES
    try:
        n = int(value)
    except ValueError as exc:  # only the name is surfaced, never the value
        raise ConfigError(f"{ENV_MAX_EVIDENCE_RETRIES} must be an integer") from exc
    if n < 0:
        raise ConfigError(f"{ENV_MAX_EVIDENCE_RETRIES} must be >= 0")
    return n


@dataclass(frozen=True)
class Settings:
    """Immutable, credential-safe view of runtime configuration."""

    meterless_base_url: Optional[str] = None
    meterless_model: Optional[str] = None
    zetaris_rest_url: Optional[str] = None
    zetaris_org_id: Optional[str] = None
    sample_mode: bool = False
    max_evidence_retries: int = DEFAULT_MAX_EVIDENCE_RETRIES
    # Secrets: excluded from the generated repr to avoid leakage.
    meterless_runtime_token: Optional[str] = field(default=None, repr=False)
    zetaris_api_key: Optional[str] = field(default=None, repr=False)

    @classmethod
    def from_environ(
        cls, environ: Optional[Mapping[str, str]] = None
    ) -> "Settings":
        """Build ``Settings`` from an environment mapping (default: os.environ).

        Reads only canonical names; legacy aliases are ignored. At module import
        time, `load_dotenv(override=False)` populates os.environ from a local
        .env file (values never logged/exposed; real env vars take precedence).
        Tests inject a custom mapping to avoid reading the developer .env.
        """
        env = os.environ if environ is None else environ
        return cls(
            meterless_base_url=env.get(ENV_METERLESS_BASE_URL),
            meterless_model=env.get(ENV_METERLESS_MODEL),
            zetaris_rest_url=env.get(ENV_ZETARIS_REST_URL),
            zetaris_org_id=env.get(ENV_ZETARIS_ORG_ID),
            sample_mode=_parse_bool(env.get(ENV_SAMPLE_MODE)),
            max_evidence_retries=_parse_retries(env.get(ENV_MAX_EVIDENCE_RETRIES)),
            meterless_runtime_token=env.get(ENV_METERLESS_RUNTIME_TOKEN),
            zetaris_api_key=env.get(ENV_ZETARIS_API_KEY),
        )

    def missing_for_live(self) -> tuple[str, ...]:
        """Canonical NAMES required for live mode but currently unset."""
        lookup = {
            ENV_METERLESS_BASE_URL: self.meterless_base_url,
            ENV_METERLESS_RUNTIME_TOKEN: self.meterless_runtime_token,
            ENV_METERLESS_MODEL: self.meterless_model,
            ENV_ZETARIS_REST_URL: self.zetaris_rest_url,
            ENV_ZETARIS_ORG_ID: self.zetaris_org_id,
            ENV_ZETARIS_API_KEY: self.zetaris_api_key,
        }
        return tuple(name for name in LIVE_REQUIRED_ENV_NAMES if not lookup[name])

    def validate_for_mode(self) -> None:
        """Sample mode needs no credentials; live mode fails with NAMES only."""
        if self.sample_mode:
            return
        missing = self.missing_for_live()
        if missing:
            raise ConfigError(
                "missing required environment variables for live mode: "
                + ", ".join(missing)
            )

    def redacted_status(self) -> dict[str, str]:
        """Report configuration WITHOUT exposing any secret value."""
        return {
            ENV_METERLESS_BASE_URL: _presence(self.meterless_base_url),
            ENV_METERLESS_RUNTIME_TOKEN: _presence(self.meterless_runtime_token),
            ENV_METERLESS_MODEL: _presence(self.meterless_model),
            ENV_ZETARIS_REST_URL: _presence(self.zetaris_rest_url),
            ENV_ZETARIS_ORG_ID: _presence(self.zetaris_org_id),
            ENV_ZETARIS_API_KEY: _presence(self.zetaris_api_key),
            ENV_SAMPLE_MODE: str(self.sample_mode),
            ENV_MAX_EVIDENCE_RETRIES: str(self.max_evidence_retries),
        }
