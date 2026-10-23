"""Fixture integrity tests — validate the synthetic hero data against the contract.

Reads ``data/fixtures/*.csv`` directly (no adapter, no network). These are the
ground-truth guarantees later phases (agent pipeline + evaluator) rely on:
referential integrity, the DATA_CONTRACT §9 validation rules, and the §10 hero
subset that grounds H4 and rejects H1-H3.
"""
from __future__ import annotations

import csv
from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[1] / "data" / "fixtures"


def _load(table: str) -> list[dict[str, str]]:
    with (FIXTURES / f"{table}.csv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _one(rows: list[dict[str, str]], key: str, value: str) -> dict[str, str]:
    matches = [r for r in rows if r[key] == value]
    assert len(matches) == 1, f"expected exactly one {key}={value}"
    return matches[0]


def test_all_hero_datasets_present_and_synthetic() -> None:
    meta = _load("dataset_meta")
    tables = {row["table"] for row in meta}
    for required in (
        "contracts",
        "invoices",
        "deliveries",
        "acceptance_records",
        "communications",
        "compliance_items",
        "payment_status",
    ):
        assert required in tables
    assert all(row["synthetic"] == "true" for row in meta)


def test_hero_invoice_grounds_revenue_and_rejects_h3() -> None:
    invoice = _one(_load("invoices"), "invoice_id", "INV-004")
    assert invoice["amount_tzs"] == "126000000"
    assert invoice["status"] == "submitted"
    # On time -> not late -> rejects H3.
    assert invoice["submitted_date"] <= invoice["required_submission_date"]


def test_hero_delivery_and_acceptance_reject_h1_h2() -> None:
    delivery = _one(_load("deliveries"), "delivery_id", "DEL-009")
    assert delivery["status"] == "complete" and delivery["delivered_date"]
    cert = _one(_load("acceptance_records"), "certificate_id", "CERT-018")
    assert cert["status"] == "issued" and cert["accepted_date"]


def test_compliance_item_grounds_h4() -> None:
    item = _one(_load("compliance_items"), "item_id", "CMP-005")
    assert item["required"] == "true"
    assert item["submitted"] == "false"
    assert item["status"] == "outstanding"
    assert item["document_type"] == "tax_clearance"
    assert item["clause_ref"] == "CLAUSE-7.2"


def test_communication_corroborates_but_is_not_sole_proof() -> None:
    msg = _one(_load("communications"), "message_id", "MSG-037")
    assert msg["references_requirement"] == "true"
    assert msg["direction"] == "inbound"


def test_payment_status_confirms_unpaid_and_h5_block() -> None:
    payment = _one(_load("payment_status"), "payment_id", "PAY-011")
    assert payment["stage"] in {"under_review", "held"}
    assert payment["amount_paid_tzs"] == "0"
    assert payment["external_block_reason"]


def test_referential_integrity_contract_id_resolves() -> None:
    contracts = {row["contract_id"] for row in _load("contracts")}
    assert "CTR-001" in contracts
    for table, fk in (
        ("invoices", "contract_id"),
        ("deliveries", "contract_id"),
        ("acceptance_records", "contract_id"),
        ("communications", "contract_id"),
        ("compliance_items", "contract_id"),
        ("payment_status", "contract_id"),
    ):
        for row in _load(table):
            assert row[fk] in contracts, f"orphan {fk} in {table}"


def test_validation_rules_hold_across_fixtures() -> None:
    invoices = {row["invoice_id"]: row for row in _load("invoices")}
    payments = _load("payment_status")
    for payment in payments:
        if payment["stage"] == "paid":
            assert int(payment["amount_paid_tzs"]) > 0
            assert invoices[payment["invoice_id"]]["status"] == "paid"
    # A submitted compliance item must carry a submitted_date.
    for item in _load("compliance_items"):
        if item["submitted"] == "true":
            assert item["submitted_date"]
