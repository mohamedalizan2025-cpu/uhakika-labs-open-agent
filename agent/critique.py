"""Model-critique validation boundary — defensive hardening of a future seam.

Phase 6 routes narrative critique from Nemotron (through Nightshift) into the
EvaluatorAgent. A critique is an untrusted **model output**, so it must never be
allowed to override a conclusion the deterministic evidence rules derived. This
module locks that contract down now:

- A critique may only carry a ``confidence`` (clamped to ``[0, 1]``) and a short
  ``note``. There is deliberately **no** ``status`` field — supported / rejected /
  insufficient come only from the evidence, so a model cannot flip a verdict.
- A malformed or unparsable critique, or one targeting an unknown hypothesis, is
  **ignored** (the rule-derived verdicts are returned untouched) rather than trusted.
- Nothing here reads credentials, environment, or the network.

The helpers are pure and side-effect free so the boundary is unit-testable in
isolation from any live runtime.
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, field_validator

from agent.evaluator_agent import HypothesisVerdict
from agent.models import HypothesisId


def clamp_confidence(value: object, fallback: float = 0.0) -> float:
    """Bound a model-supplied confidence into ``[0, 1]``.

    Non-numeric or NaN input is not trusted: it collapses to ``fallback``.
    """
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return fallback
    if number != number:  # NaN
        return fallback
    return max(0.0, min(1.0, number))


class ModelCritique(BaseModel):
    """A single untrusted critique for one hypothesis (no status by design)."""

    hypothesis_id: HypothesisId
    confidence: float = 0.0
    note: str = ""

    @field_validator("confidence")
    @classmethod
    def _bound_confidence(cls, value: float) -> float:
        return clamp_confidence(value, 0.0)


def parse_critique(payload: object) -> Optional[ModelCritique]:
    """Validate an untrusted critique payload; return ``None`` when malformed."""
    try:
        return ModelCritique.model_validate(payload)
    except Exception:  # ValidationError and any coercion failure -> ignore
        return None


def apply_critique(
    verdicts: list[HypothesisVerdict], payload: object
) -> tuple[list[HypothesisVerdict], bool]:
    """Safely fold one model critique into rule-derived verdicts.

    Returns ``(verdicts, applied)``. A verdict's ``status`` is never changed —
    only its ``confidence`` is adjusted (clamped to ``[0, 1]``) on the matched
    hypothesis. A malformed payload, or one naming an unknown hypothesis, is
    ignored (``applied`` is ``False`` and the verdicts are returned unchanged).
    """
    critique = parse_critique(payload)
    if critique is None:
        return list(verdicts), False

    known = {v.id for v in verdicts}
    if critique.hypothesis_id not in known:
        return list(verdicts), False

    applied = False
    result: list[HypothesisVerdict] = []
    for verdict in verdicts:
        if verdict.id == critique.hypothesis_id:
            result.append(
                HypothesisVerdict(
                    id=verdict.id,
                    status=verdict.status,  # evidence-derived, never model-set
                    reason=verdict.reason,
                    confidence=clamp_confidence(critique.confidence, verdict.confidence),
                    evidence_ids=list(verdict.evidence_ids),
                )
            )
            applied = True
        else:
            result.append(verdict)
    return result, applied
