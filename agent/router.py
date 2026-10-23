"""Intent Router stage — a routing stage, NOT one of the three core agents.

The live path must be powered by the required Meterless Engine **Scout Intent**
(AGENTS.md §2.2/§7, ARCHITECTURE.md §8). Scout Intent is not yet wired or verified,
so this deterministic fallback router classifies the request and selects the
investigation playbook. Its label is always ``fallback`` — it is never presented as
Scout Intent, and no provider/engine is claimed.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RoutedTask:
    playbook: str
    label: str  # always "fallback" until Scout Intent is verified for live use
    invoice_id: str


_REVENUE_ASSURANCE_TRIGGERS = ("unpaid", "not paid", "hasn't been paid", "payment", "why")


class IntentRouter:
    """Selects the revenue-assurance playbook for a receivable question."""

    def route(self, question: str, invoice_id: str) -> RoutedTask:
        text = (question or "").lower()
        if any(token in text for token in _REVENUE_ASSURANCE_TRIGGERS) or invoice_id:
            return RoutedTask(playbook="revenue_assurance", label="fallback", invoice_id=invoice_id)
        # Unknown intent still routes to the only V0 playbook, labeled honestly.
        return RoutedTask(playbook="revenue_assurance", label="fallback", invoice_id=invoice_id)
