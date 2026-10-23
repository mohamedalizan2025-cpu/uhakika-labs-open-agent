"""Evaluator + Investigator pipeline tests — grounding, anti-fabrication, retries.

No network / credentials / .env. Exercises the rule engine on hand-built evidence
bundles and a fake adapter to prove conclusions are derived from evidence, are
downgraded when evidence is removed, and that the evidence loop is bounded.
"""
from __future__ import annotations

from agent.config import ENV_MAX_EVIDENCE_RETRIES, Settings
from agent.evidence_agent import EvidenceBundle
from agent.evaluator_agent import EvaluatorAgent
from agent.investigator_agent import InvestigatorAgent
from agent.models import Evidence, RunRequest
from agent.tools_zetaris import ZetarisAdapter, ZetarisQueryResult


def _hero_bundle() -> EvidenceBundle:
    return EvidenceBundle(
        invoice={
            "invoice_id": "INV-004",
            "contract_id": "CTR-001",
            "amount_tzs": 126000000,
            "currency": "TZS",
            "submitted_date": "2025-09-15",
            "required_submission_date": "2025-09-20",
            "status": "submitted",
        },
        contract={"contract_id": "CTR-001", "clause_ref": "CLAUSE-7.2", "requires_compliance_docs": "true"},
        deliveries=[{"delivery_id": "DEL-009", "invoice_id": "INV-004", "status": "complete", "delivered_date": "2025-08-28"}],
        acceptance=[{"certificate_id": "CERT-018", "invoice_id": "INV-004", "status": "issued", "accepted_date": "2025-09-05"}],
        compliance=[
            {"item_id": "CMP-005", "invoice_id": "INV-004", "document_type": "tax_clearance", "required": "true", "submitted": "false", "status": "outstanding"},
            {"item_id": "CMP-006", "invoice_id": "INV-004", "document_type": "vat_registration", "required": "true", "submitted": "true", "status": "verified"},
        ],
        communications=[{"message_id": "MSG-037", "invoice_id": "INV-004", "references_requirement": "true", "direction": "inbound", "summary": "buyer requested tax clearance"}],
        payment={"payment_id": "PAY-011", "invoice_id": "INV-004", "stage": "under_review", "amount_paid_tzs": 0, "external_block_reason": "held pending tax clearance"},
        evidence=[Evidence(evidence_id="CMP-005", source="compliance_items", summary="tax_clearance outstanding")],
    )


def _statuses(outcome) -> dict[str, str]:
    return {v.id: v.status for v in outcome.verdicts}


def test_hero_bundle_supports_h4_and_rejects_h1_h3() -> None:
    outcome = EvaluatorAgent().evaluate(_hero_bundle())
    st = _statuses(outcome)
    assert st["H4"] == "supported"
    assert st["H1"] == "rejected"
    assert st["H2"] == "rejected"
    assert st["H3"] == "rejected"
    assert outcome.supported_cause == "H4"
    assert outcome.blocker_class == "execution_documentation"
    assert outcome.revenue_at_risk == 126000000
    # Cause cites the authoritative item, the clause, and the corroborating message.
    assert {"CMP-005", "CLAUSE-7.2", "MSG-037"} <= set(outcome.cause_evidence_ids)


def test_removing_cmp005_downgrades_h4() -> None:
    bundle = _hero_bundle()
    bundle.compliance = [c for c in bundle.compliance if c["item_id"] != "CMP-005"]
    outcome = EvaluatorAgent().evaluate(bundle)
    # H4 is no longer supported once its authoritative row is gone.
    assert _statuses(outcome)["H4"] == "rejected"
    assert outcome.supported_cause != "H4"


def test_communication_alone_is_not_proof_of_h4() -> None:
    bundle = _hero_bundle()
    bundle.compliance = []  # no compliance rows; only a corroborating message
    outcome = EvaluatorAgent().evaluate(bundle)
    assert _statuses(outcome)["H4"] == "insufficient"
    assert outcome.supported_cause != "H4"


class _FakeAdapter(ZetarisAdapter):
    """Returns fixed fixture rows so the retry loop can be observed."""

    _TABLES = {
        "invoices": (["invoice_id", "contract_id", "amount_tzs", "currency", "submitted_date", "required_submission_date", "status"], [("INV-004", "CTR-001", "126000000", "TZS", "2025-09-15", "2025-09-20", "submitted")]),
        "contracts": (["contract_id", "clause_ref", "requires_compliance_docs"], [("CTR-001", "CLAUSE-7.2", "true")]),
        "deliveries": (["delivery_id", "invoice_id", "status", "delivered_date"], [("DEL-009", "INV-004", "complete", "2025-08-28")]),
        "acceptance_records": (["certificate_id", "invoice_id", "status", "accepted_date"], [("CERT-018", "INV-004", "issued", "2025-09-05")]),
        "compliance_items": (["item_id", "invoice_id", "document_type", "required", "submitted", "status"], []),
        "communications": (["message_id", "invoice_id", "references_requirement", "direction", "summary"], []),
        "payment_status": (["payment_id", "invoice_id", "stage", "amount_paid_tzs", "external_block_reason"], [("PAY-011", "INV-004", "paid", "126000000", "")]),
    }

    def __init__(self) -> None:
        self.calls = 0

    def run_query(self, sql: str, request_id: str) -> ZetarisQueryResult:
        self.calls += 1
        table = sql.split("FROM", 1)[1].split()[0].strip()
        columns, rows = self._TABLES.get(table, ([], []))
        return ZetarisQueryResult(request_id=request_id, columns=tuple(columns), rows=tuple(rows))


def test_evidence_loop_is_bounded() -> None:
    settings = Settings.from_environ({ENV_MAX_EVIDENCE_RETRIES: "2"})
    adapter = _FakeAdapter()
    investigator = InvestigatorAgent(settings, adapter=adapter)
    response = investigator.run(
        RunRequest(question="why unpaid", invoice_id="INV-004", sample_mode=True)
    )
    # All H1-H3 rejected, H4/H5 undecided -> no supported cause -> retries up to max.
    assert response.supported_cause == "insufficient_evidence"
    evidence_passes = [e for e in response.trace if e.agent == "EvidenceAgent"]
    assert len(evidence_passes) == 3  # initial pass + 2 bounded retries
    assert max(e.retry_count for e in evidence_passes) == 2
