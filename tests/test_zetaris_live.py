"""Tests for the live Zetaris adapter boundary — NO network is performed.

Covers the credential-safe construction gate (missing config reports NAMES only),
the one-statement-per-call rule, the documented endpoint wiring, and the honest
contract gate: ``run_query`` refuses to execute (raising
``ZetarisContractNotValidatedError``) rather than invent request/response fields
that the binding contract still marks ``TBD``.
"""
from __future__ import annotations

import pytest

from agent.config import (
    ENV_ZETARIS_API_KEY,
    ENV_ZETARIS_ORG_ID,
    ENV_ZETARIS_REST_URL,
    Settings,
)
from agent.tools_zetaris import ZetarisQueryError
from agent.zetaris_live import (
    LiveZetarisAdapter,
    ZetarisContractNotValidatedError,
)

_KEY = "zetaris-live-key-never-printed"


def _live_settings() -> Settings:
    return Settings.from_environ(
        {
            ENV_ZETARIS_REST_URL: "http://localhost:8888/api/v1.0",
            ENV_ZETARIS_ORG_ID: "org-1",
            ENV_ZETARIS_API_KEY: _KEY,
        }
    )


def test_missing_config_raises_with_names_only() -> None:
    with pytest.raises(ZetarisQueryError) as exc:
        LiveZetarisAdapter(Settings.from_environ({}))
    message = str(exc.value)
    assert ENV_ZETARIS_REST_URL in message
    assert ENV_ZETARIS_ORG_ID in message
    assert ENV_ZETARIS_API_KEY in message
    # No credential value ever leaks into the error.
    assert _KEY not in message


def test_run_query_is_gated_until_contract_validated() -> None:
    adapter = LiveZetarisAdapter(_live_settings())
    with pytest.raises(ZetarisContractNotValidatedError):
        adapter.run_query("SELECT 1", "req-live")


def test_one_statement_rule_enforced_before_the_gate() -> None:
    adapter = LiveZetarisAdapter(_live_settings())
    # A batched statement fails the one-statement rule (not the contract gate).
    with pytest.raises(ZetarisQueryError) as exc:
        adapter.run_query("SELECT 1; SELECT 2", "req-batch")
    assert not isinstance(exc.value, ZetarisContractNotValidatedError)


def test_endpoint_wiring_is_documented_not_hardcoded_secret() -> None:
    adapter = LiveZetarisAdapter(_live_settings())
    assert adapter.run_endpoint == "http://localhost:8888/api/v1.0/sql-editor/sqls/run"
