"""Model-critique boundary tests — defensive, evidence-over-model precedence.

Proves a model critique can only adjust confidence (clamped to [0,1]) and can
NEVER change an evidence-derived status, and that malformed / mis-targeted
critiques are ignored rather than trusted. No network, no credentials, no model.
"""
from __future__ import annotations

from agent.critique import (
    ModelCritique,
    apply_critique,
    clamp_confidence,
    parse_critique,
)
from agent.evaluator_agent import HypothesisVerdict


def _verdicts() -> list[HypothesisVerdict]:
    return [
        HypothesisVerdict("H4", "supported", "required compliance outstanding", 0.8, ["CMP-005"]),
        HypothesisVerdict("H1", "rejected", "complete delivery exists", 0.85, ["DEL-009"]),
    ]


# --- clamp_confidence --------------------------------------------------
def test_clamp_bounds_and_rejects_junk() -> None:
    assert clamp_confidence(1.5) == 1.0
    assert clamp_confidence(-0.2) == 0.0
    assert clamp_confidence(0.42) == 0.42
    assert clamp_confidence("not a number", 0.3) == 0.3
    assert clamp_confidence(None, 0.1) == 0.1
    assert clamp_confidence(float("nan"), 0.0) == 0.0


# --- parse_critique ----------------------------------------------------
def test_parse_clamps_confidence_on_ingest() -> None:
    critique = parse_critique({"hypothesis_id": "H4", "confidence": 1.7})
    assert isinstance(critique, ModelCritique)
    assert critique is not None and critique.confidence == 1.0


def test_parse_rejects_unknown_hypothesis_id() -> None:
    assert parse_critique({"hypothesis_id": "H9", "confidence": 0.5}) is None


def test_parse_rejects_non_numeric_confidence() -> None:
    assert parse_critique({"hypothesis_id": "H4", "confidence": "high"}) is None


def test_parse_rejects_non_mapping_payload() -> None:
    assert parse_critique("just a string") is None
    assert parse_critique(None) is None


# --- apply_critique ----------------------------------------------------
def test_apply_adjusts_confidence_but_never_status() -> None:
    verdicts, applied = apply_critique(
        _verdicts(), {"hypothesis_id": "H4", "confidence": 0.45}
    )
    assert applied is True
    h4 = next(v for v in verdicts if v.id == "H4")
    assert h4.confidence == 0.45
    # The evidence-derived status is untouched by the model.
    assert h4.status == "supported"


def test_apply_ignores_model_attempt_to_set_status() -> None:
    # A model cannot smuggle a status flip in — extra fields are dropped and the
    # status stays whatever the evidence rules decided.
    verdicts, applied = apply_critique(
        _verdicts(),
        {"hypothesis_id": "H4", "confidence": 0.9, "status": "rejected"},
    )
    assert applied is True
    h4 = next(v for v in verdicts if v.id == "H4")
    assert h4.status == "supported"


def test_apply_clamps_out_of_range_confidence() -> None:
    verdicts, applied = apply_critique(
        _verdicts(), {"hypothesis_id": "H1", "confidence": 5.0}
    )
    assert applied is True
    h1 = next(v for v in verdicts if v.id == "H1")
    assert h1.confidence == 1.0


def test_apply_ignores_malformed_critique() -> None:
    original = _verdicts()
    verdicts, applied = apply_critique(original, {"hypothesis_id": "H4", "confidence": "abc"})
    assert applied is False
    assert [v.confidence for v in verdicts] == [0.8, 0.85]


def test_apply_ignores_unknown_target_hypothesis() -> None:
    # Valid critique shape, but names a hypothesis not present in the verdicts.
    verdicts, applied = apply_critique(
        _verdicts(), {"hypothesis_id": "H5", "confidence": 0.9}
    )
    assert applied is False
    assert [v.confidence for v in verdicts] == [0.8, 0.85]


def test_apply_does_not_mutate_input_verdicts() -> None:
    original = _verdicts()
    _, _ = apply_critique(original, {"hypothesis_id": "H4", "confidence": 0.2})
    assert original[0].confidence == 0.8  # source list left intact
