"""Credential-free boundary tests for the Zetaris and Nightshift interfaces.

Verifies the adapter contracts WITHOUT any network, credentials, or ``.env``:
- the abstract adapters cannot be instantiated directly,
- a minimal in-test stub satisfies the contract,
- a Zetaris result carries a fresh request id and reports emptiness correctly.
"""
from __future__ import annotations

import pytest

from agent.llm import CompletionRequest, CompletionResult, NightshiftAdapter
from agent.tools_zetaris import ZetarisAdapter, ZetarisQueryResult


class _StubZetaris(ZetarisAdapter):
    """Records calls so we can assert the one-statement / fresh-id contract."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def run_query(self, sql: str, request_id: str) -> ZetarisQueryResult:
        self.calls.append((sql, request_id))
        return ZetarisQueryResult(
            request_id=request_id, columns=("x",), rows=((1,),)
        )


class _StubNightshift(NightshiftAdapter):
    def __init__(self, route_name: str) -> None:
        self.route_name = route_name

    def complete(self, request: CompletionRequest) -> CompletionResult:
        return CompletionResult(text="ok", model_route=self.route_name)


def test_zetaris_base_is_abstract() -> None:
    with pytest.raises(TypeError):
        ZetarisAdapter()  # type: ignore[abstract]


def test_zetaris_stub_returns_fresh_request_id_per_call() -> None:
    adapter = _StubZetaris()
    r1 = adapter.run_query("SELECT a FROM t", "req-1")
    r2 = adapter.run_query("SELECT b FROM t", "req-2")
    assert r1.request_id == "req-1"
    assert r2.request_id == "req-2"
    assert r1.request_id != r2.request_id
    assert len(adapter.calls) == 2


def test_zetaris_empty_result_is_meaningful_not_an_error() -> None:
    empty = ZetarisQueryResult(request_id="req-3", columns=(), rows=())
    assert empty.is_empty
    assert empty.row_count == 0


def test_nightshift_base_is_abstract() -> None:
    with pytest.raises(TypeError):
        NightshiftAdapter()  # type: ignore[abstract]


def test_nightshift_stub_complete_reports_route_name() -> None:
    adapter = _StubNightshift("configured-model-route")
    result = adapter.complete(CompletionRequest(prompt="hi"))
    assert isinstance(result, CompletionResult)
    assert result.model_route == "configured-model-route"
