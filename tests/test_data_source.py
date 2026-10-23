"""Factory selection tests — mode routes to the right adapter, no network."""
from __future__ import annotations

from agent.config import (
    ENV_SAMPLE_MODE,
    ENV_ZETARIS_API_KEY,
    ENV_ZETARIS_ORG_ID,
    ENV_ZETARIS_REST_URL,
    Settings,
)
from agent.data_source import build_zetaris_adapter
from agent.zetaris_live import LiveZetarisAdapter
from agent.zetaris_sample import SampleZetarisAdapter


def test_sample_mode_selects_sample_adapter() -> None:
    settings = Settings.from_environ({ENV_SAMPLE_MODE: "true"})
    assert isinstance(build_zetaris_adapter(settings), SampleZetarisAdapter)


def test_live_mode_selects_live_adapter_when_configured() -> None:
    settings = Settings.from_environ(
        {
            ENV_ZETARIS_REST_URL: "http://localhost:8888/api/v1.0",
            ENV_ZETARIS_ORG_ID: "org-1",
            ENV_ZETARIS_API_KEY: "configured-not-printed",
        }
    )
    assert isinstance(build_zetaris_adapter(settings), LiveZetarisAdapter)
