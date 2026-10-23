"""LIVE Zetaris adapter boundary (HTTP transport via httpx) — contract-gated.

Targets the mandatory live data layer described in AGENTS.md §4 / DATA_CONTRACT.md
§8: base ``ZETARIS_REST_URL`` (expected local value ``http://localhost:8888/api/v1.0``),
SQL endpoint ``/sql-editor/sqls/run``, one statement per call, a fresh request ID
per query, credentials sourced ONLY from canonical env-driven ``Settings``.

HONEST STATUS — why execution is deferred:
- The exact request-body keys and response-body shape are still ``TBD`` in the
  binding contract (``DATA_CONTRACT.md`` §8) and BUILD_PLAN Phase 3 explicitly
  forbids inventing them: they MUST be validated against a live, running Zetaris
  instance (or verified client code) before use.
- No verified Zetaris client exists in the repo (``smoke_test.py`` is empty) and
  the live service cannot be reached here because the canonical Zetaris variables
  are not yet populated by the owner (the agent never reads ``.env``).
- Therefore this boundary implements everything that is safe and known (the
  credential-safe construction gate reporting NAMES only, the one-statement-per-
  call rule, and the documented endpoint/base wiring) and raises a clear,
  structured ``ZetarisContractNotValidatedError`` on ``run_query`` instead of
  fabricating payload/response fields. Live querying is a genuine blocker to be
  cleared once the contract is validated against the running service.

The credential-free ``SampleZetarisAdapter`` exercises the SAME pipeline today, so
nothing downstream depends on the live path being validated yet.
"""
from __future__ import annotations

from typing import Optional

import httpx

from agent.config import (
    ENV_ZETARIS_API_KEY,
    ENV_ZETARIS_ORG_ID,
    ENV_ZETARIS_REST_URL,
    Settings,
)
from agent.tools_zetaris import ZetarisAdapter, ZetarisQueryError, ZetarisQueryResult

# Known, contract-documented path segment (not a secret).
SQL_RUN_PATH = "/sql-editor/sqls/run"
DEFAULT_TIMEOUT_SECONDS = 30.0


class ZetarisContractNotValidatedError(ZetarisQueryError):
    """Raised when a live query is attempted before the SQL contract is validated.

    This is an operational gate, not a failure: it reports that the request/
    response payload fields must be confirmed against the running Zetaris service
    (per DATA_CONTRACT.md §8) before the live adapter may execute a statement.
    """


class LiveZetarisAdapter(ZetarisAdapter):
    """Live data-layer boundary. Requires canonical Zetaris configuration.

    Construction is credential-safe: missing canonical variables raise with NAMES
    only. Actual ``run_query`` is gated until the Lightning-SQL payload/response
    contract is validated against a live service (see module docstring).
    """

    def __init__(
        self,
        settings: Settings,
        *,
        client: Optional[httpx.Client] = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        missing = _missing_config_names(settings)
        if missing:
            # NAMES only — never any value.
            raise ZetarisQueryError(
                "live Zetaris mode requires canonical configuration; missing: "
                + ", ".join(missing)
            )
        self._base_url = str(settings.zetaris_rest_url).rstrip("/")
        self._org_id = str(settings.zetaris_org_id)
        self._api_key = str(settings.zetaris_api_key)
        # Client is created lazily only after the contract is validated; nothing
        # here opens a network connection at construction time.
        self._client = client
        self._timeout = timeout

    @property
    def run_endpoint(self) -> str:
        return f"{self._base_url}{SQL_RUN_PATH}"

    def run_query(self, sql: str, request_id: str) -> ZetarisQueryResult:
        statement = sql.strip()
        # Enforce the one-statement-per-call rule at the live boundary.
        if ";" in statement.rstrip(";"):
            raise ZetarisQueryError("only one SQL statement per call is allowed")
        # Do not fabricate request/response fields: require live validation first.
        raise ZetarisContractNotValidatedError(
            "live Zetaris query blocked until the Lightning-SQL request/response "
            "contract is validated against the running service (DATA_CONTRACT.md "
            "section 8 fields remain TBD); the sample adapter runs the same "
            "pipeline credential-free"
        )


def _missing_config_names(settings: Settings) -> tuple[str, ...]:
    lookup = {
        ENV_ZETARIS_REST_URL: settings.zetaris_rest_url,
        ENV_ZETARIS_ORG_ID: settings.zetaris_org_id,
        ENV_ZETARIS_API_KEY: settings.zetaris_api_key,
    }
    return tuple(name for name, value in lookup.items() if not value)
