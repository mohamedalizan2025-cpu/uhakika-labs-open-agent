"""Regression tests for Phase 6A readiness semantics.

Proves:
1. Empty environment defaults to sample mode.
2. Six populated variables alone do NOT imply live_ready.
3. Missing variables are reported by NAME only (never values).
4. An implemented-but-unverified adapter is NOT operational.
5. Live requests NEVER silently use the sample adapter.
6. No secret value appears in health/error/trace output.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from agent.capabilities import CapabilityRegistry
from agent.config import Settings
from agent.main import create_app

_SECRET = "sk-TEST-SECRET-NEVER-SHOW-THIS"


def _empty_env() -> Settings:
    """Settings from an empty environment (no vars set)."""
    return Settings.from_environ({})


def _full_live_env() -> Settings:
    """Settings with ALL six live vars populated (but integrations NOT operational)."""
    return Settings.from_environ({
        "METERLESS_BASE_URL": "http://runtime.invalid/v1",
        "METERLESS_RUNTIME_TOKEN": _SECRET,
        "METERLESS_MODEL": "test-model",
        "ZETARIS_REST_URL": "http://data.invalid/api/v1.0",
        "ZETARIS_ORG_ID": "org-test",
        "ZETARIS_API_KEY": _SECRET,
        "SAMPLE_MODE": "false",
    })


class TestSafeDefault:
    """Finding 6: SAMPLE_MODE absent = sample mode."""

    def test_empty_env_sample_mode(self):
        s = _empty_env()
        assert s.sample_mode is True

    def test_empty_env_default_mode_is_sample(self):
        app = create_app(settings=_empty_env())
        client = TestClient(app)
        body = client.get("/health").json()
        assert body["default_mode"] == "sample"

    def test_explicit_live_via_env(self):
        s = Settings.from_environ({"SAMPLE_MODE": "false"})
        assert s.sample_mode is False

    def test_explicit_truthy_sample(self):
        s = Settings.from_environ({"SAMPLE_MODE": "true"})
        assert s.sample_mode is True


class TestLiveReadyRequiresOperational:
    """Populated variables alone must NOT make live_ready true."""

    def test_full_vars_but_not_operational(self):
        s = _full_live_env()
        caps = CapabilityRegistry()
        caps.update_configuration(s)
        # configured may be true, but NOT operational
        assert caps.zetaris.configured is True
        assert caps.nightshift.configured is True
        assert caps.live_ready is False

    def test_live_ready_with_incomplete_operational(self):
        caps = CapabilityRegistry()
        caps.zetaris.operational = True
        caps.nightshift.operational = True
        # scout intent NOT verified
        caps.scout_intent_verified = False
        assert caps.live_ready is False

    def test_live_ready_all_operational(self):
        caps = CapabilityRegistry()
        caps.zetaris.operational = True
        caps.nightshift.operational = True
        caps.scout_intent_verified = True
        assert caps.live_ready is True

    def test_health_reports_live_ready_false(self):
        app = create_app(settings=_full_live_env())
        client = TestClient(app)
        body = client.get("/health").json()
        # Even with all vars populated, live_ready is False (nothing operational)
        assert body["live_ready"] is False


class TestMissingNamesOnly:
    """Missing variables reported by NAME, never values."""

    def test_health_missing_env_names(self):
        app = create_app(settings=_empty_env())
        client = TestClient(app)
        body = client.get("/health").json()
        names = body["missing_env_names"]
        assert isinstance(names, list)
        assert len(names) > 0
        # All items are strings matching canonical variable names
        for n in names:
            assert isinstance(n, str)
            assert not n.startswith("http")
            assert not n.startswith("sk-")

    def test_zetaris_integration_missing_names(self):
        app = create_app(settings=_empty_env())
        client = TestClient(app)
        body = client.get("/health").json()
        zt = body["integrations"]["zetaris"]
        for name in zt["missing_env_names"]:
            assert name.startswith("ZETARIS_")


class TestUnverifiedAdapterNotOperational:
    """A code path that exists but hasn't been verified is NOT operational."""

    def test_default_registry_all_false(self):
        caps = CapabilityRegistry()
        assert caps.zetaris.operational is False
        assert caps.nightshift.operational is False
        assert caps.scout_intent_verified is False
        assert caps.live_ready is False


class TestNoSilentFallback:
    """Live requests never silently fall back to sample mode."""

    def test_live_returns_503(self):
        app = create_app(settings=_empty_env())
        client = TestClient(app)
        response = client.post("/run", json={
            "question": "why unpaid",
            "invoice_id": "INV-004",
            "sample_mode": False,
        })
        assert response.status_code == 503
        detail = response.json()["detail"]
        assert detail["error"] == "live_mode_not_operational"
        assert detail["live_ready"] is False

    def test_live_with_full_config_still_503(self):
        """Even with all vars populated, live returns 503 (not operational)."""
        app = create_app(settings=_full_live_env())
        client = TestClient(app)
        response = client.post("/run", json={
            "question": "why unpaid",
            "invoice_id": "INV-004",
            "sample_mode": False,
        })
        assert response.status_code == 503


class TestNoSecretInOutput:
    """Secrets never appear in health, error, or trace output."""

    def test_health_no_secret(self):
        s = _full_live_env()
        app = create_app(settings=s)
        client = TestClient(app)
        body_text = client.get("/health").text
        assert _SECRET not in body_text

    def test_error_no_secret(self):
        s = _full_live_env()
        app = create_app(settings=s)
        client = TestClient(app)
        response = client.post("/run", json={
            "question": "test",
            "invoice_id": "INV-001",
            "sample_mode": False,
        })
        assert _SECRET not in response.text
