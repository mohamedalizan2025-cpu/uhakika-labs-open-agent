"""Credential-free SAMPLE implementation of the Zetaris adapter.

Implements the SAME ``ZetarisAdapter`` contract the EvidenceAgent will depend on,
but resolves single Lightning-SQL statements against the synthetic CSV fixtures in
``data/fixtures/`` — no network, no credentials, no ``.env``. This lets the real
pipeline run end-to-end in ``SAMPLE_MODE`` while live Zetaris access is configured.

Supported statement subset (intentionally small and deterministic):
- ``SELECT 1``  — liveness smoke (returns one row).
- ``SELECT <cols> FROM <table> [WHERE <col> = <value> [AND ...]]``
  where ``<cols>`` is ``*`` or a comma list, ``<value>`` is a single-quoted string
  or a bare word (matched case-insensitively for booleans/ids).

Rules honored: ONE statement per call (semicolon batching rejected); the caller's
fresh ``request_id`` is echoed back; "no matching rows" is a valid empty result,
not an error.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Optional

from agent.tools_zetaris import ZetarisAdapter, ZetarisQueryError, ZetarisQueryResult

_DEFAULT_FIXTURES_DIR = Path(__file__).resolve().parents[1] / "data" / "fixtures"

_TABLE_RE = re.compile(
    r"^SELECT\s+(?P<cols>.+?)\s+FROM\s+(?P<table>[A-Za-z_][A-Za-z0-9_]*)"
    r"(?:\s+WHERE\s+(?P<where>.+?))?$",
    re.IGNORECASE | re.DOTALL,
)
_SMOKE_RE = re.compile(r"^SELECT\s+1\s*$", re.IGNORECASE)
_CONDITION_SPLIT_RE = re.compile(r"\s+AND\s+", re.IGNORECASE)
_CONDITION_RE = re.compile(
    r"^(?P<col>[A-Za-z_][A-Za-z0-9_]*)\s*(?P<op>=|!=|<>)\s*(?P<val>.+)$"
)


class SampleZetarisAdapter(ZetarisAdapter):
    """Read-only, credential-free adapter backed by CSV fixtures."""

    def __init__(self, fixtures_dir: Optional[Path] = None) -> None:
        self._fixtures_dir = Path(fixtures_dir or _DEFAULT_FIXTURES_DIR)
        self._cache: dict[str, tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]] = {}

    # --- table loading ---------------------------------------------------
    def _load_table(self, table: str) -> tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]:
        if table in self._cache:
            return self._cache[table]
        path = self._fixtures_dir / f"{table}.csv"
        if not path.is_file():
            raise ZetarisQueryError(f"unknown table: {table!r}")
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            rows = [row for row in reader if row]
        columns = tuple(rows[0])
        data = tuple(tuple(row) for row in rows[1:])
        self._cache[table] = (columns, data)
        return self._cache[table]

    # --- query execution -------------------------------------------------
    def run_query(self, sql: str, request_id: str) -> ZetarisQueryResult:
        statement = self._normalize(sql)

        if _SMOKE_RE.match(statement):
            return ZetarisQueryResult(
                request_id=request_id, columns=("ok",), rows=(("1",),)
            )

        match = _TABLE_RE.match(statement)
        if not match:
            raise ZetarisQueryError("unsupported query shape for the sample adapter")

        columns, data = self._load_table(match.group("table"))
        selected = self._select_columns(match.group("cols"), columns)
        indices = [columns.index(name) for name in selected]

        predicates = self._parse_where(match.group("where"), columns)
        out_rows = []
        for row in data:
            if all(test(row, columns) for test in predicates):
                out_rows.append(tuple(row[i] for i in indices))
        return ZetarisQueryResult(
            request_id=request_id, columns=selected, rows=tuple(out_rows)
        )

    # --- helpers ---------------------------------------------------------
    @staticmethod
    def _normalize(sql: str) -> str:
        statement = sql.strip()
        # Reject semicolon-batched statements (one statement per call).
        if ";" in statement:
            if statement.count(";") > 1 or not statement.endswith(";"):
                raise ZetarisQueryError(
                    "only one SQL statement per call is allowed"
                )
            statement = statement[:-1].strip()
        return statement

    @staticmethod
    def _select_columns(spec: str, columns: tuple[str, ...]) -> tuple[str, ...]:
        spec = spec.strip()
        if spec == "*":
            return columns
        lowered = {name.lower(): name for name in columns}
        selected = []
        for raw in spec.split(","):
            name = raw.strip()
            if name.lower() not in lowered:
                raise ZetarisQueryError(f"unknown column: {name!r}")
            selected.append(lowered[name.lower()])
        return tuple(selected)

    @staticmethod
    def _parse_where(clause: Optional[str], columns: tuple[str, ...]):
        if not clause:
            return []
        lowered = {name.lower(): name for name in columns}
        tests = []
        for part in _CONDITION_SPLIT_RE.split(clause.strip()):
            match = _CONDITION_RE.match(part.strip())
            if not match:
                raise ZetarisQueryError(f"unsupported WHERE condition: {part!r}")
            col = match.group("col")
            if col.lower() not in lowered:
                raise ZetarisQueryError(f"unknown column: {col!r}")
            index = columns.index(lowered[col.lower()])
            op = match.group("op")
            value = _unquote(match.group("val"))
            tests.append(_make_test(index, op, value))
        return tests


def _unquote(token: str) -> str:
    token = token.strip()
    if len(token) >= 2 and token[0] == token[-1] and token[0] in ("'", '"'):
        return token[1:-1]
    return token


def _make_test(index: int, op: str, value: str):
    expected = value.strip()
    ignore_case = expected.lower() in {"true", "false"}

    def test(row: tuple[str, ...], _columns: tuple[str, ...]) -> bool:
        actual = row[index]
        if ignore_case:
            lhs, rhs = actual.strip().lower(), expected.lower()
        else:
            lhs, rhs = actual, expected
        if op == "=":
            return lhs == rhs
        return lhs != rhs  # '!=' or '<>'

    return test
