"""Competing-hypothesis catalog.

These are the *questions* InvestigatorAgent considers — identifiers and labels
only. No hypothesis is marked supported/rejected here; every status is derived at
runtime by EvaluatorAgent from evidence (AGENTS.md §2.8 — never hardcode a
conclusion). The mapping to authoritative evidence is in DATA_CONTRACT.md §11.
"""
from __future__ import annotations

from agent.models import Hypothesis, HypothesisId

# (id, human label). Order is the fixed consideration order H1..H5.
HYPOTHESIS_LABELS: tuple[tuple[HypothesisId, str], ...] = (
    ("H1", "Delivery incomplete"),
    ("H2", "Acceptance certificate missing"),
    ("H3", "Invoice submitted late"),
    ("H4", "Required compliance / tax evidence missing"),
    ("H5", "External buyer / payment-stage blockage"),
)


def initial_hypotheses() -> list[Hypothesis]:
    """Fresh, all-`investigating` hypotheses for a new case."""
    return [
        Hypothesis(id=hypo_id, label=label, status="investigating")
        for hypo_id, label in HYPOTHESIS_LABELS
    ]
