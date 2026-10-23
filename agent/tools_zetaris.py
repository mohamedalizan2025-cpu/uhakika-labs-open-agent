"""Zetaris data-layer adapter INTERFACE (no live client yet).

Zetaris is the mandatory data layer (AGENTS.md §2.1, §4, §6). This module defines
ONLY the contract the EvidenceAgent will depend on. Concrete live and credential-
free sample clients are implemented in later approved phases (BUILD_PLAN Phase 3).

Binding rules any future implementation must honor:
- All business evidence is retrieved through Zetaris; no bypasses.
- One SQL statement per call; a FRESH request ID per query.
- Base URL / auth come from injected configuration; never hardcoded, never printed.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


class ZetarisQueryError(Exception):
    """Raised for a malformed or unsupported query / adapter misconfiguration.

    Messages are operational only and never contain a credential value.
    """


@dataclass(frozen=True)
class ZetarisQueryResult:
    """A grounded, credential-free result set for a single Zetaris query."""

    request_id: str
    columns: tuple[str, ...]
    rows: tuple[tuple[Any, ...], ...]

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def is_empty(self) -> bool:
        return not self.rows


class ZetarisAdapter(ABC):
    """Abstract interface for executing a single Lightning-SQL statement."""

    @abstractmethod
    def run_query(self, sql: str, request_id: str) -> ZetarisQueryResult:
        """Run exactly ONE SQL statement and return a grounded result set.

        Implementations must:
        - use a FRESH, unique ``request_id`` per call (reuse is a bug),
        - accept a single statement (no semicolon-batched statements),
        - treat an empty result as meaningful ("no rows"), not as an error,
        - never embed or print credentials.
        """
        raise NotImplementedError
