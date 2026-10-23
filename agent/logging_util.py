"""Sanitized operational logging + in-memory trace sink.

Rules (AGENTS.md §9 / ARCHITECTURE.md §11):
- Emit **operational traces only** — actions, tools, evidence references and
  decisions. Never chain-of-thought / private reasoning.
- Never log a credential or secret value. Values are referenced by NAME only.
- Every conclusion entry should cite evidence IDs.

This module provides a redacting formatter and a small structured trace list.
Actual trace production happens in the agent pipeline (a later phase).
"""
from __future__ import annotations

import logging
from typing import Any, Optional

LOGGER_NAME = "uhakika"

# Canonical field set for one operational-trace entry (see ARCHITECTURE §11).
TRACE_FIELDS = (
    "ts",
    "agent",
    "action",
    "tool",
    "source_result_summary",
    "decision",
    "confidence",
    "retry_count",
    "model_route",
    "evidence_ids",
)


class _NoSecretFilter(logging.Filter):
    """Defense-in-depth: drop any record that looks like it embeds a secret.

    Guards against accidental leakage of a credential value into a log line.
    """

    _FORBIDDEN_MARKERS = (
        "METERLESS_RUNTIME_TOKEN",
        "ZETARIS_API_KEY",
        "BEGIN PRIVATE KEY",
        "ghp_",
        "gho_",
        "sk-",
    )

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: D401
        message = str(record.getMessage())
        return not any(marker in message for marker in self._FORBIDDEN_MARKERS)


def get_logger() -> logging.Logger:
    """Return the app logger with a redacting filter installed (idempotent)."""
    logger = logging.getLogger(LOGGER_NAME)
    if not getattr(logger, "_uhakika_configured", False):
        logger.addFilter(_NoSecretFilter())
        logger.setLevel(logging.INFO)
        logger._uhakika_configured = True  # type: ignore[attr-defined]
    return logger


class TraceLogger:
    """Collects operational-trace entries in memory for a single run."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []
        self._logger = get_logger()

    def add(
        self,
        *,
        ts: str,
        agent: str,
        action: str,
        tool: Optional[str] = None,
        source_result_summary: Optional[str] = None,
        decision: Optional[str] = None,
        confidence: Optional[float] = None,
        retry_count: int = 0,
        model_route: Optional[str] = None,
        evidence_ids: Optional[list[str]] = None,
    ) -> None:
        """Append one operational-trace entry and log it (sanitized)."""
        entry = {
            "ts": ts,
            "agent": agent,
            "action": action,
            "tool": tool,
            "source_result_summary": source_result_summary,
            "decision": decision,
            "confidence": confidence,
            "retry_count": retry_count,
            "model_route": model_route,
            "evidence_ids": list(evidence_ids or []),
        }
        self._entries.append(entry)
        # Log only the safe, non-secret descriptive fields.
        self._logger.info(
            "trace agent=%s action=%s evidence_ids=%s",
            agent,
            action,
            entry["evidence_ids"],
        )

    def entries(self) -> list[dict[str, Any]]:
        """Return a copy of the collected operational trace."""
        return list(self._entries)
