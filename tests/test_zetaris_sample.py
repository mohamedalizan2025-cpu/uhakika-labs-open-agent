"""Credential-free tests for the sample Zetaris adapter (mini-SQL over fixtures).

No network, no credentials, no ``.env`` — everything resolves against the synthetic
CSV fixtures. Locks the hero evidence retrieval path used by later phases.
"""
from __future__ import annotations

import pytest

from agent.tools_zetaris import ZetarisQueryError
from agent.zetaris_sample import SampleZetarisAdapter


@pytest.fixture()
def adapter() -> SampleZetarisAdapter:
    return SampleZetarisAdapter()


def test_smoke_select_one(adapter: SampleZetarisAdapter) -> None:
    result = adapter.run_query("SELECT 1", "smoke-1")
    assert result.request_id == "smoke-1"
    assert result.row_count == 1
    assert result.rows == (("1",),)


def test_hero_invoice_row(adapter: SampleZetarisAdapter) -> None:
    result = adapter.run_query(
        "SELECT invoice_id, contract_id, amount_tzs, submitted_date, "
        "required_submission_date, status FROM invoices "
        "WHERE invoice_id = 'INV-004'",
        "req-inv",
    )
    assert result.columns == (
        "invoice_id",
        "contract_id",
        "amount_tzs",
        "submitted_date",
        "required_submission_date",
        "status",
    )
    assert result.row_count == 1
    row = dict(zip(result.columns, result.rows[0]))
    assert row["amount_tzs"] == "126000000"
    assert row["contract_id"] == "CTR-001"
    # On-time submission rejects H3 (submitted_date <= required_submission_date).
    assert row["submitted_date"] <= row["required_submission_date"]


def test_missing_compliance_evidence_grounds_h4(adapter: SampleZetarisAdapter) -> None:
    result = adapter.run_query(
        "SELECT item_id, document_type, required, submitted, clause_ref "
        "FROM compliance_items WHERE required = true AND submitted = false",
        "req-cmp",
    )
    ids = {row[0] for row in result.rows}
    assert ids == {"CMP-005"}
    row = dict(zip(result.columns, result.rows[0]))
    assert row["document_type"] == "tax_clearance"
    assert row["clause_ref"] == "CLAUSE-7.2"


def test_select_star_returns_all_columns(adapter: SampleZetarisAdapter) -> None:
    result = adapter.run_query(
        "SELECT * FROM acceptance_records WHERE certificate_id = 'CERT-018'",
        "req-cert",
    )
    assert "status" in result.columns
    row = dict(zip(result.columns, result.rows[0]))
    assert row["status"] == "issued"
    assert row["accepted_date"]  # present -> rejects H2


def test_no_rows_is_meaningful_not_an_error(adapter: SampleZetarisAdapter) -> None:
    result = adapter.run_query(
        "SELECT invoice_id FROM invoices WHERE invoice_id = 'NOPE'", "req-empty"
    )
    assert result.is_empty
    assert result.row_count == 0


def test_fresh_request_id_is_echoed_per_call(adapter: SampleZetarisAdapter) -> None:
    a = adapter.run_query("SELECT 1", "id-1")
    b = adapter.run_query("SELECT 1", "id-2")
    assert a.request_id == "id-1"
    assert b.request_id == "id-2"
    assert a.request_id != b.request_id


def test_unknown_table_raises(adapter: SampleZetarisAdapter) -> None:
    with pytest.raises(ZetarisQueryError):
        adapter.run_query("SELECT * FROM does_not_exist", "req-x")


def test_semicolon_batching_is_rejected(adapter: SampleZetarisAdapter) -> None:
    with pytest.raises(ZetarisQueryError):
        adapter.run_query("SELECT 1; SELECT 2", "req-batch")


def test_trailing_single_semicolon_is_allowed(adapter: SampleZetarisAdapter) -> None:
    result = adapter.run_query("SELECT 1;", "req-semi")
    assert result.row_count == 1
