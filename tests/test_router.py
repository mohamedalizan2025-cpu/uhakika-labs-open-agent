"""Intent Router tests — deterministic fallback, never mislabeled Scout Intent."""
from __future__ import annotations

from agent.router import IntentRouter


def test_routes_to_revenue_assurance_playbook() -> None:
    task = IntentRouter().route("Why hasn't invoice INV-004 been paid?", "INV-004")
    assert task.playbook == "revenue_assurance"
    assert task.invoice_id == "INV-004"


def test_router_is_always_labeled_fallback_never_scout_intent() -> None:
    router = IntentRouter()
    for question, invoice in [
        ("Why is INV-004 unpaid?", "INV-004"),
        ("some unrelated text", ""),
        ("payment status?", "INV-001"),
    ]:
        task = router.route(question, invoice)
        assert task.label == "fallback"
        assert "scout" not in task.label.lower()
