"""InvestigatorAgent — frames the case and orchestrates the evidence loop.

Owns the shared case state, generates competing hypotheses, drives
EvidenceAgent → EvaluatorAgent within a BOUNDED retry loop, then derives the
supported cause, revenue at risk, a recommendation that cites evidence, and a
human-approval gate. It records an operational trace (actions/decisions only — never
chain-of-thought) via the sanitized TraceLogger.

Conclusions are computed from evidence on every run (no stored hero answer).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from agent.config import Settings
from agent.data_source import build_zetaris_adapter
from agent.evaluator_agent import EvaluatorAgent, EvaluatorOutcome
from agent.evidence_agent import EvidenceAgent
from agent.hypotheses import initial_hypotheses
from agent.logging_util import TraceLogger
from agent.models import (
    RejectedHypothesis,
    RunRequest,
    RunResponse,
    TraceEntry,
)
from agent.router import IntentRouter
from agent.tools_zetaris import ZetarisAdapter, ZetarisQueryError

_LABEL_BY_ID = {
    "H1": "Delivery incomplete",
    "H2": "Acceptance certificate missing",
    "H3": "Invoice submitted late",
    "H4": "Required compliance / tax evidence missing",
    "H5": "External buyer / payment-stage blockage",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class InvestigatorAgent:
    """Coordinates routing, evidence, evaluation, and the approval gate."""

    def __init__(self, settings: Settings, adapter: Optional[ZetarisAdapter] = None) -> None:
        self._settings = settings
        self._router = IntentRouter()
        self._adapter = adapter if adapter is not None else build_zetaris_adapter(settings)
        self._evidence_agent = EvidenceAgent(self._adapter)
        self._evaluator = EvaluatorAgent()

    def run(self, request: RunRequest) -> RunResponse:
        trace = TraceLogger()
        case_id = f"case-{uuid.uuid4().hex[:12]}"

        routed = self._router.route(request.question, request.invoice_id)
        trace.add(
            ts=_now(),
            agent="IntentRouter",
            action="route",
            tool="intent_router",
            decision=f"playbook={routed.playbook} label={routed.label}",
            model_route=None,
        )

        hypotheses = initial_hypotheses()
        trace.add(
            ts=_now(),
            agent="InvestigatorAgent",
            action="generate_hypotheses",
            decision=f"framed {len(hypotheses)} hypotheses H1-H5",
        )

        max_retries = self._settings.max_evidence_retries
        outcome: Optional[EvaluatorOutcome] = None
        evidence_records = []
        retries = 0
        while True:
            try:
                bundle = self._evidence_agent.gather(routed.invoice_id)
            except ZetarisQueryError as exc:
                # Adapter / retrieval failure is an honest operating state, not a
                # crash. Record it operationally (type name only — never the raw
                # message, which could carry configured identifiers) and stop with
                # an insufficient result rather than fabricate a conclusion.
                note = (
                    f"evidence retrieval failed ({type(exc).__name__}) — "
                    "insufficient evidence to reach a grounded conclusion"
                )
                trace.add(
                    ts=_now(),
                    agent="EvidenceAgent",
                    action="retrieve_evidence",
                    tool="zetaris.run_query",
                    decision="adapter_error",
                    source_result_summary=note,
                    retry_count=retries,
                )
                evidence_records = []
                outcome = EvaluatorOutcome(
                    verdicts=[],
                    supported_cause=None,
                    blocker_class=None,
                    revenue_at_risk=0,
                    currency="TZS",
                    cause_evidence_ids=[],
                    insufficient=True,
                    resolution_note=note,
                )
                break
            evidence_records = bundle.evidence
            trace.add(
                ts=_now(),
                agent="EvidenceAgent",
                action="retrieve_evidence",
                tool="zetaris.run_query",
                source_result_summary=f"{bundle.query_count} queries; {len(bundle.evidence)} cited records",
                retry_count=retries,
                evidence_ids=bundle.evidence_ids(),
            )

            outcome = self._evaluator.evaluate(bundle)
            trace.add(
                ts=_now(),
                agent="EvaluatorAgent",
                action="evaluate_hypotheses",
                decision=self._verdict_summary(outcome),
                confidence=outcome and self._cause_confidence(outcome),
                retry_count=retries,
                model_route=None,
                evidence_ids=outcome.cause_evidence_ids,
            )

            # Stop when a supported cause is found, or when the anchor is missing
            # (insufficient), or when the bounded retry budget is exhausted.
            if (
                outcome.supported_cause is not None
                or outcome.insufficient
                or retries >= max_retries
            ):
                break
            retries += 1

        assert outcome is not None  # loop runs at least once
        response = self._compose(case_id, outcome, evidence_records, retries)
        trace.add(
            ts=_now(),
            agent="InvestigatorAgent",
            action="draft_recommendation",
            decision=f"approval_status={response.approval_status}",
            evidence_ids=[e.evidence_id for e in response.evidence[:1]],
        )
        # Operational trace only (actions/decisions); typed as TraceEntry records.
        response.trace = [TraceEntry(**entry) for entry in trace.entries()]
        return response

    # --- composition -----------------------------------------------------
    def _compose(
        self,
        case_id: str,
        outcome: EvaluatorOutcome,
        evidence_records,
        retries: int,
    ) -> RunResponse:
        rejected = [
            RejectedHypothesis(id=v.id, reason=v.reason)
            for v in outcome.verdicts
            if v.status == "rejected"
        ]

        if outcome.insufficient or outcome.supported_cause is None:
            supported_cause = "insufficient_evidence"
            recommendation = outcome.resolution_note or (
                "insufficient evidence to reach a grounded conclusion"
            )
            approval_status = "not_required"
        else:
            supported_cause = _LABEL_BY_ID[outcome.supported_cause]
            recommendation = self._recommendation(outcome)
            approval_status = "pending"  # consequential action needs a human

        return RunResponse(
            case_id=case_id,
            revenue_at_risk=outcome.revenue_at_risk,
            supported_cause=supported_cause,
            blocker_class=outcome.blocker_class,
            rejected_hypotheses=rejected,
            evidence=list(evidence_records),
            recommendation=recommendation,
            approval_status=approval_status,
            trace=[],  # filled by caller
        )

    @staticmethod
    def _recommendation(outcome: EvaluatorOutcome) -> str:
        ids = ", ".join(outcome.cause_evidence_ids) or "cited evidence"
        currency = outcome.currency
        risk = outcome.revenue_at_risk
        cause = outcome.supported_cause
        if cause == "H4":
            return (
                f"Resolve the outstanding required compliance/tax documentation "
                f"({ids}) and resubmit to release {currency} {risk} at risk."
            )
        if cause == "H5":
            return (
                f"Escalate the external buyer/payment blockage ({ids}); "
                f"{currency} {risk} at risk pending the buyer."
            )
        return (
            f"Address the supported cause {cause} evidenced by {ids}; "
            f"{currency} {risk} at risk."
        )

    @staticmethod
    def _verdict_summary(outcome: EvaluatorOutcome) -> str:
        supported = [v.id for v in outcome.verdicts if v.status == "supported"]
        rejected = [v.id for v in outcome.verdicts if v.status == "rejected"]
        insufficient = [v.id for v in outcome.verdicts if v.status == "insufficient"]
        return (
            f"supported={supported or '[]'} rejected={rejected} "
            f"insufficient={insufficient} cause={outcome.supported_cause}"
        )

    @staticmethod
    def _cause_confidence(outcome: EvaluatorOutcome) -> Optional[float]:
        for v in outcome.verdicts:
            if v.id == outcome.supported_cause:
                return v.confidence
        return None
