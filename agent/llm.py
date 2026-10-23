"""Meterless Nightshift runtime adapter INTERFACE (no live client yet).

Nightshift is the product AI runtime (AGENTS.md §2.2, §4). Nemotron model routing
is configurable and must never be hardcoded (AGENTS.md §2.3). This module defines
ONLY the contract; concrete live + credential-free sample adapters arrive in a
later approved phase.

Base URL, model route, and token are supplied via injected ``Settings``
(env-driven). No endpoint, model ID, or token is embedded here.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CompletionRequest:
    """A single inference request handed to the runtime."""

    prompt: str
    # Optional knobs; concrete defaults are decided at implementation time.
    max_tokens: Optional[int] = None


@dataclass(frozen=True)
class CompletionResult:
    """A credential-free completion outcome.

    ``model_route`` records the configured route NAME as used (never a secret).
    """

    text: str
    model_route: str


class NightshiftAdapter(ABC):
    """Abstract interface for product-runtime inference through Nightshift."""

    @abstractmethod
    def complete(self, request: CompletionRequest) -> CompletionResult:
        """Return a completion from the configured Nightshift/Nemotron route.

        Implementations must run through Nightshift (never Qwen/Qoder build
        tooling), keep the model route configurable, and never print or embed
        credentials.
        """
        raise NotImplementedError
