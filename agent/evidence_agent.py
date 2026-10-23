"""EvidenceAgent — retrieves and normalizes evidence via the Zetaris adapter only.

Responsibility (ARCHITECTURE.md §3): turn each hypothesis's information need into
single-statement Zetaris queries (a FRESH request ID per query), then normalize the
returned rows into typed facts plus cited ``Evidence`` records. It never invents a
row: "no rows" is captured as an explicit, queryable absence.

No business conclusion is made here — that is EvaluatorAgent's job.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

from agent.models import Evidence
from agent.tools_zetaris import ZetarisAdapter

# Columns whose values are whole-number minor/amount units and are cast to int.
_INT_FIELDS = {"amount_tzs", "amount_paid_tzs", "quantity", "value_tzs"}


@dataclass
class EvidenceBundle:
    """Typed facts retrieved for one investigation, plus cited evidence."""

    invoice: Optional[dict[str, Any]] = None
    contract: Optional[dict[str, Any]] = None
    deliveries: list[dict[str, Any]] = field(default_factory=list)
    acceptance: list[dict[str, Any]] = field(default_factory=list)
    compliance: list[dict[str, Any]] = field(default_factory=list)
    communications: list[dict[str, Any]] = field(default_factory=list)
    payment: Optional[dict[str, Any]] = None
    evidence: list[Evidence] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    query_count: int = 0

    def evidence_ids(self) -> list[str]:
        return [ev.evidence_id for ev in self.evidence]


class EvidenceAgent:
    """Fetches and normalizes evidence for a case through ``ZetarisAdapter``."""

    def __init__(self, adapter: ZetarisAdapter) -> None:
        self._adapter = adapter

    # --- public API ------------------------------------------------------
    def gather(self, invoice_id: str) -> EvidenceBundle:
        bundle = EvidenceBundle()

        invoice_rows = self._query(
            "invoices", "invoice_id", invoice_id, bundle
        )
        if not invoice_rows:
            bundle.notes.append(f"no invoice row for {invoice_id!r}")
            return bundle
        bundle.invoice = invoice_rows[0]
        self._add_evidence(bundle, "invoices", bundle.invoice, "invoice_id")

        contract_id = bundle.invoice.get("contract_id")
        if contract_id:
            contract_rows = self._query(
                "contracts", "contract_id", contract_id, bundle
            )
            if contract_rows:
                bundle.contract = contract_rows[0]
                self._add_evidence(bundle, "contracts", bundle.contract, "contract_id")
                clause = bundle.contract.get("clause_ref")
                if clause:
                    bundle.evidence.append(
                        Evidence(
                            evidence_id=clause,
                            source="contracts.clause_ref",
                            summary=f"Governing clause citation {clause}",
                        )
                    )

        for table, key, store in (
            ("deliveries", "invoice_id", "deliveries"),
            ("acceptance_records", "invoice_id", "acceptance"),
            ("compliance_items", "contract_id", "compliance"),
            ("communications", "invoice_id", "communications"),
        ):
            lookup = invoice_id if key == "invoice_id" else contract_id
            if not lookup:
                continue
            rows = self._query(table, key, lookup, bundle)
            getattr(bundle, store).extend(rows)
            if not rows:
                bundle.notes.append(f"no {table} rows for {lookup!r}")
            for row in rows:
                self._add_evidence(bundle, table, row, _primary_key(table))

        if contract_id:
            payment_rows = self._query(
                "payment_status", "invoice_id", invoice_id, bundle
            )
            if payment_rows:
                bundle.payment = payment_rows[0]
                self._add_evidence(bundle, "payment_status", bundle.payment, "payment_id")

        return bundle

    # --- helpers ---------------------------------------------------------
    def _query(
        self, table: str, key: str, value: str, bundle: EvidenceBundle
    ) -> list[dict[str, Any]]:
        sql = f"SELECT * FROM {table} WHERE {key} = '{_escape(value)}'"
        result = self._adapter.run_query(sql, request_id=uuid.uuid4().hex)
        bundle.query_count += 1
        return [_cast(dict(zip(result.columns, row))) for row in result.rows]

    @staticmethod
    def _add_evidence(
        bundle: EvidenceBundle, table: str, row: dict[str, Any], pk: str
    ) -> None:
        evidence_id = str(row.get(pk, f"{table}-{len(bundle.evidence)}"))
        summary = _summarize(table, row)
        bundle.evidence.append(
            Evidence(evidence_id=evidence_id, source=table, summary=summary)
        )


_PRIMARY_KEYS = {
    "invoices": "invoice_id",
    "contracts": "contract_id",
    "deliveries": "delivery_id",
    "acceptance_records": "certificate_id",
    "compliance_items": "item_id",
    "communications": "message_id",
    "payment_status": "payment_id",
}


def _primary_key(table: str) -> str:
    return _PRIMARY_KEYS.get(table, "contract_id")


def _escape(value: str) -> str:
    # Minimal guard for the single-token id used in WHERE equality.
    return value.replace("'", "")


def _cast(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    for field_name in list(out):
        if field_name in _INT_FIELDS and out[field_name] not in ("", None):
            try:
                out[field_name] = int(float(out[field_name]))
            except (TypeError, ValueError):
                pass
    return out


def _summarize(table: str, row: dict[str, Any]) -> str:
    if table == "invoices":
        return f"Invoice {row.get('invoice_id')} amount {row.get('amount_tzs')} {row.get('currency', '')} status {row.get('status')}".strip()
    if table == "compliance_items":
        return (
            f"{row.get('document_type')} required={row.get('required')} "
            f"submitted={row.get('submitted')} status={row.get('status')}"
        )
    if table == "deliveries":
        return f"Delivery {row.get('delivery_id')} status {row.get('status')} delivered_date {row.get('delivered_date')}"
    if table == "acceptance_records":
        return f"Certificate {row.get('certificate_id')} status {row.get('status')} accepted_date {row.get('accepted_date')}"
    if table == "communications":
        return f"Message {row.get('message_id')} ({row.get('direction')}) references_requirement={row.get('references_requirement')}: {row.get('summary')}"
    if table == "payment_status":
        return f"Payment {row.get('payment_id')} stage {row.get('stage')} reason={row.get('external_block_reason')}"
    if table == "contracts":
        return f"Contract {row.get('contract_id')} requires_compliance_docs={row.get('requires_compliance_docs')} clause={row.get('clause_ref')}"
    return f"{table} record"
