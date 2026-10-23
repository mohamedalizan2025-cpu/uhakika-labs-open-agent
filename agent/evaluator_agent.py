"""EvaluatorAgent — scores each hypothesis against retrieved evidence.

Applies the authoritative DATA_CONTRACT.md §11 hypothesis→data rules to the facts
the EvidenceAgent gathered. A hypothesis is:
- **supported** only when its authoritative evidence is present,
- **rejected** with a reason tied to evidence (or its documented absence),
- **insufficient** when the data needed to decide was not retrieved.

Live mode reaches Nemotron through Nightshift for narrative critique (Phase 6);
the grounding rules themselves are deterministic so conclusions never depend on an
unverified model, and this sample pass makes NO model/provider claim. Nothing here
stores a hero answer — outcomes are computed from the supplied evidence each run.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from agent.evidence_agent import EvidenceBundle
from agent.models import BlockerClass, HypothesisId

# Primary-cause priority: the most actionable supplier/documentation cause wins;
# external payment blockage (H5) is treated as a downstream symptom.
_CAUSE_PRIORITY: tuple[HypothesisId, ...] = ("H4", "H1", "H2", "H3", "H5")

# Deterministic confidence levels for the rule-based verdicts (not model output).
_CONF_SUPPORTED = 0.8
_CONF_REJECTED = 0.85
_CONF_INSUFFICIENT = 0.2

# Which blocker class each supported cause implies.
_BLOCKER_BY_CAUSE: dict[str, BlockerClass] = {
    "H1": "supplier_controllable",
    "H2": "execution_documentation",
    "H3": "supplier_controllable",
    "H4": "execution_documentation",
    "H5": "external_payment",
}


@dataclass
class HypothesisVerdict:
    id: HypothesisId
    status: str  # supported | rejected | insufficient
    reason: str
    confidence: float
    evidence_ids: list[str] = field(default_factory=list)


@dataclass
class EvaluatorOutcome:
    verdicts: list[HypothesisVerdict]
    supported_cause: Optional[HypothesisId]
    blocker_class: Optional[BlockerClass]
    revenue_at_risk: int
    currency: str
    cause_evidence_ids: list[str]
    insufficient: bool
    resolution_note: Optional[str]
    # True only when a validated model critique adjusted a verdict's confidence.
    # It never changes a status — those stay evidence-derived (see agent.critique).
    critique_applied: bool = False


class EvaluatorAgent:
    """Derives per-hypothesis verdicts and the supported cause from evidence."""

    def evaluate(
        self, bundle: EvidenceBundle, critique: Optional[object] = None
    ) -> EvaluatorOutcome:
        invoice_id = (bundle.invoice or {}).get("invoice_id")

        verdicts = [
            self._h1(bundle, invoice_id),
            self._h2(bundle, invoice_id),
            self._h3(bundle),
            self._h4(bundle, invoice_id),
            self._h5(bundle),
        ]

        # Optionally fold in a model critique. Imported lazily so this module
        # (which critique.py depends on) has no import-time cycle. The critique
        # may only adjust confidence; statuses stay evidence-derived, and a
        # malformed / unknown-target critique is ignored.
        critique_applied = False
        if critique is not None:
            from agent.critique import apply_critique

            verdicts, critique_applied = apply_critique(verdicts, critique)

        by_id = {v.id: v for v in verdicts}
        supported = [v for v in verdicts if v.status == "supported"]
        insufficient = [v for v in verdicts if v.status == "insufficient"]

        supported_cause: Optional[HypothesisId] = None
        blocker_class: Optional[BlockerClass] = None
        cause_evidence_ids: list[str] = []
        for hypo_id in _CAUSE_PRIORITY:
            if hypo_id in {v.id for v in supported}:
                supported_cause = hypo_id
                blocker_class = _BLOCKER_BY_CAUSE[hypo_id]
                cause_evidence_ids = list(dict.fromkeys(by_id[hypo_id].evidence_ids))
                break

        revenue_at_risk, currency = self._revenue_at_risk(bundle)

        # Insufficient only when we cannot reach any supported cause AND the anchor
        # evidence is missing (e.g. unknown invoice).
        resolution_note: Optional[str] = None
        is_insufficient = supported_cause is None and bundle.invoice is None
        if is_insufficient:
            resolution_note = (
                "no invoice record retrieved — supply a valid invoice_id and the "
                "linked contract/compliance data to resolve the investigation"
            )

        return EvaluatorOutcome(
            verdicts=verdicts,
            supported_cause=supported_cause,
            blocker_class=blocker_class,
            revenue_at_risk=revenue_at_risk,
            currency=currency,
            cause_evidence_ids=cause_evidence_ids,
            insufficient=is_insufficient,
            resolution_note=resolution_note,
            critique_applied=critique_applied,
        )

    # --- per-hypothesis rules -------------------------------------------
    def _h1(self, bundle: EvidenceBundle, invoice_id: Optional[str]) -> HypothesisVerdict:
        if bundle.invoice is None:
            return HypothesisVerdict("H1", "insufficient", "no invoice anchor", _CONF_INSUFFICIENT)
        relevant = [d for d in bundle.deliveries if d.get("invoice_id") == invoice_id]
        if not relevant:
            return HypothesisVerdict("H1", "insufficient", "no delivery rows retrieved for this invoice", _CONF_INSUFFICIENT)
        complete = [d for d in relevant if str(d.get("status")).lower() == "complete" and d.get("delivered_date")]
        if complete:
            ids = [str(d.get("delivery_id")) for d in complete]
            return HypothesisVerdict("H1", "rejected", "a complete delivery exists", _CONF_REJECTED, ids)
        ids = [str(d.get("delivery_id")) for d in relevant]
        return HypothesisVerdict("H1", "supported", "no complete delivery for this invoice", _CONF_SUPPORTED, ids)

    def _h2(self, bundle: EvidenceBundle, invoice_id: Optional[str]) -> HypothesisVerdict:
        if bundle.invoice is None:
            return HypothesisVerdict("H2", "insufficient", "no invoice anchor", _CONF_INSUFFICIENT)
        relevant = [a for a in bundle.acceptance if a.get("invoice_id") == invoice_id]
        issued = [a for a in relevant if str(a.get("status")).lower() == "issued" and a.get("accepted_date")]
        if issued:
            ids = [str(a.get("certificate_id")) for a in issued]
            return HypothesisVerdict("H2", "rejected", "an issued acceptance certificate exists", _CONF_REJECTED, ids)
        if not relevant:
            return HypothesisVerdict("H2", "supported", "no acceptance certificate retrieved (missing acceptance)", _CONF_SUPPORTED, [])
        ids = [str(a.get("certificate_id")) for a in relevant]
        return HypothesisVerdict("H2", "supported", "no issued acceptance certificate", _CONF_SUPPORTED, ids)

    def _h3(self, bundle: EvidenceBundle) -> HypothesisVerdict:
        invoice = bundle.invoice
        if invoice is None:
            return HypothesisVerdict("H3", "insufficient", "no invoice anchor", _CONF_INSUFFICIENT)
        submitted = invoice.get("submitted_date")
        required = invoice.get("required_submission_date")
        ids = [str(invoice.get("invoice_id"))]
        if not submitted:
            return HypothesisVerdict("H3", "insufficient", "invoice not yet submitted (null submitted_date)", _CONF_INSUFFICIENT, ids)
        # Dates are ISO strings -> lexicographic compare is chronological.
        if required and str(submitted) > str(required):
            return HypothesisVerdict("H3", "supported", "submitted_date is after required_submission_date", _CONF_SUPPORTED, ids)
        return HypothesisVerdict("H3", "rejected", "submitted on or before the required date", _CONF_REJECTED, ids)

    def _h4(self, bundle: EvidenceBundle, invoice_id: Optional[str]) -> HypothesisVerdict:
        if bundle.invoice is None:
            return HypothesisVerdict("H4", "insufficient", "no invoice anchor", _CONF_INSUFFICIENT)
        relevant = [
            c for c in bundle.compliance
            if c.get("invoice_id") in ("", None) or c.get("invoice_id") == invoice_id
        ]
        outstanding = [
            c for c in relevant
            if str(c.get("required")).lower() == "true"
            and str(c.get("submitted")).lower() == "false"
        ]
        if outstanding:
            ids = [str(c.get("item_id")) for c in outstanding]
            clause = (bundle.contract or {}).get("clause_ref")
            if clause:
                ids.append(str(clause))
            corroborating = [
                m.get("message_id")
                for m in bundle.communications
                if str(m.get("references_requirement")).lower() == "true"
            ]
            ids.extend(str(c) for c in corroborating if c)
            return HypothesisVerdict(
                "H4", "supported",
                "a required compliance item is not submitted (authoritative) "
                "+ buyer request corroborates",
                _CONF_SUPPORTED, list(dict.fromkeys(ids)),
            )
        if relevant and all(
            str(c.get("required")).lower() != "true"
            or str(c.get("submitted")).lower() == "true"
            for c in relevant
        ):
            ids = [str(c.get("item_id")) for c in relevant]
            return HypothesisVerdict("H4", "rejected", "all required compliance items are submitted", _CONF_REJECTED, ids)
        return HypothesisVerdict("H4", "insufficient", "no compliance_items retrieved to decide", _CONF_INSUFFICIENT)

    def _h5(self, bundle: EvidenceBundle) -> HypothesisVerdict:
        payment = bundle.payment
        if not payment:
            return HypothesisVerdict("H5", "insufficient", "no payment_status retrieved", _CONF_INSUFFICIENT)
        stage = str(payment.get("stage")).lower()
        ids = [str(payment.get("payment_id"))]
        if stage == "paid":
            return HypothesisVerdict("H5", "rejected", "payment already made", _CONF_REJECTED, ids)
        if stage in {"held", "under_review", "rejected", "not_submitted"} and payment.get("external_block_reason"):
            return HypothesisVerdict("H5", "supported", "payment held with an explicit external block reason", _CONF_SUPPORTED, ids)
        return HypothesisVerdict("H5", "insufficient", f"payment stage {stage!r} is not decisive", _CONF_INSUFFICIENT, ids)

    @staticmethod
    def _revenue_at_risk(bundle: EvidenceBundle) -> tuple[int, str]:
        invoice = bundle.invoice or {}
        amount = _as_int(invoice.get("amount_tzs"))
        paid = _as_int((bundle.payment or {}).get("amount_paid_tzs"))
        currency = str(invoice.get("currency") or "TZS")
        return max(amount - paid, 0), currency


def _as_int(value: Any) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0
