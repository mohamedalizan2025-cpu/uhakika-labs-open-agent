"""Credential-free tests for the canonical configuration module (pytest).

Never touches `.env`: configuration is exercised against an in-memory mapping.
Proves: legacy aliases ignored, canonical names load, secrets masked, sample mode
starts without credentials, live mode reports missing NAMES only.
"""
from __future__ import annotations

import pytest

from agent.config import (
    CANONICAL_ENV_NAMES,
    ConfigError,
    ENV_METERLESS_MODEL,
    ENV_METERLESS_RUNTIME_TOKEN,
    ENV_METERLESS_BASE_URL,
    ENV_SAMPLE_MODE,
    ENV_ZETARIS_API_KEY,
    ENV_ZETARIS_ORG_ID,
    ENV_ZETARIS_REST_URL,
    LEGACY_ENV_NAMES,
    SECRET_ENV_NAMES,
    Settings,
)

_SECRET = "sentinel-runtime-token-never-leak"
_APIKEY = "sentinel-zetaris-key-never-leak"


def test_canonical_names_are_exactly_the_eight() -> None:
    assert set(CANONICAL_ENV_NAMES) == {
        ENV_METERLESS_BASE_URL,
        ENV_METERLESS_RUNTIME_TOKEN,
        ENV_METERLESS_MODEL,
        ENV_ZETARIS_REST_URL,
        ENV_ZETARIS_ORG_ID,
        ENV_ZETARIS_API_KEY,
        ENV_SAMPLE_MODE,
        "MAX_EVIDENCE_RETRIES",
    }


def test_legacy_aliases_are_ignored_and_not_migrated() -> None:
    env = {
        "METERLESS_API_KEY": _SECRET,
        "NEMOTRON_MODEL": "legacy-model",
        "ZETARIS_BASE_URL": "https://legacy.invalid",
    }
    s = Settings.from_environ(env)
    # Legacy values must not populate any canonical field.
    assert s.meterless_runtime_token is None
    assert s.meterless_model is None
    assert s.zetaris_rest_url is None
    assert s.sample_mode is True  # absent SAMPLE_MODE defaults to sample (safe)
    assert _SECRET not in repr(s)
    assert "legacy-model" not in repr(s)
    assert "https://legacy.invalid" not in str(s.redacted_status())
    assert LEGACY_ENV_NAMES == frozenset(
        {"METERLESS_API_KEY", "NEMOTRON_MODEL", "ZETARIS_BASE_URL"}
    )


def test_canonical_names_load() -> None:
    env = {
        ENV_METERLESS_BASE_URL: "https://runtime.invalid/config",
        ENV_METERLESS_RUNTIME_TOKEN: _SECRET,
        ENV_METERLESS_MODEL: "configured-model-route",
        ENV_ZETARIS_REST_URL: "http://localhost:8888/api/v1.0",
        ENV_ZETARIS_ORG_ID: "org-123",
        ENV_ZETARIS_API_KEY: _APIKEY,
        ENV_SAMPLE_MODE: "true",
        "MAX_EVIDENCE_RETRIES": "5",
    }
    s = Settings.from_environ(env)
    assert s.meterless_base_url == "https://runtime.invalid/config"
    assert s.meterless_model == "configured-model-route"
    assert s.zetaris_org_id == "org-123"
    assert s.sample_mode is True
    assert s.max_evidence_retries == 5


def test_missing_values_are_none_not_hardcoded() -> None:
    s = Settings.from_environ({})
    assert s.meterless_base_url is None
    assert s.meterless_model is None
    assert s.zetaris_rest_url is None
    assert s.sample_mode is True  # absent SAMPLE_MODE defaults to sample (safe)
    assert s.max_evidence_retries == 3


def test_secrets_never_appear_in_repr_or_status() -> None:
    env = {ENV_METERLESS_RUNTIME_TOKEN: _SECRET, ENV_ZETARIS_API_KEY: _APIKEY}
    s = Settings.from_environ(env)
    assert _SECRET not in repr(s)
    assert _APIKEY not in repr(s)
    assert _SECRET not in str(s.redacted_status())
    assert _APIKEY not in str(s.redacted_status())
    assert SECRET_ENV_NAMES == frozenset(
        {ENV_METERLESS_RUNTIME_TOKEN, ENV_ZETARIS_API_KEY}
    )


def test_sample_mode_starts_without_credentials() -> None:
    s = Settings.from_environ({ENV_SAMPLE_MODE: "1"})
    assert s.sample_mode is True
    # No credentials present, yet sample mode validates cleanly.
    s.validate_for_mode()


def test_live_mode_error_reports_names_only() -> None:
    # Explicitly set SAMPLE_MODE=false to attempt live validation.
    s = Settings.from_environ({
        ENV_METERLESS_RUNTIME_TOKEN: _SECRET,
        ENV_SAMPLE_MODE: "false",
    })
    with pytest.raises(ConfigError) as exc:
        s.validate_for_mode()
    message = str(exc.value)
    assert _SECRET not in message
    assert ENV_METERLESS_BASE_URL in message
    assert ENV_ZETARIS_API_KEY in message
