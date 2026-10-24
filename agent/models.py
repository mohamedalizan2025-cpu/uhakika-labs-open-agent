"""Domain + API data models (Pydantic contracts).

These define the shape of a case and the `POST /run` request/response contract
(see ARCHITECTURE.md §10 and DATA_CONTRACT.md §11). The endpoints ARE implemented
(Phase 4+) in agent/main.py; these schemas are the live contract used by both
backend and frontend. No business logic or conclusions live in this module —
schemas only. No field may hardcode a credential or model route.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

# --- Controlled vocabularies (aligned with DATA_CONTRACT.md §5 / §11). ---
HypothesisId = Literal["H1", "H2", "H3", "H4", "H5"]
HypothesisStatus = Literal[
    "investigating", "supported", "rejected", "insufficient"
]
BlockerClass = Literal[
    "supplier_controllable", "execution_documentation", "external_payment"
]
ApprovalStatus = Literal["not_required", "pending", "approved", "rejected"]


class Evidence(BaseModel):
    """A single cited evidence record (traceable by ID)."""

    evidence_id: str
    source: str
    summary: str


class Hypothesis(BaseModel):
    """A competing hypothesis under investigation."""

    id: HypothesisId
    label: str
    status: HypothesisStatus = "investigating"
    reason: Optional[str] = None
    evidence_ids: list[str] = Field(default_factory=list)


class TraceEntry(BaseModel):
    """One operational-trace entry. Actions/decisions only — never reasoning."""

    ts: str
    agent: str
    action: str
    tool: Optional[str] = None
    source_result_summary: Optional[str] = None
    decision: Optional[str] = None
    confidence: Optional[float] = None
    retry_count: int = 0
    model_route: Optional[str] = None
    evidence_ids: list[str] = Field(default_factory=list)


class RunRequest(BaseModel):
    """Request contract for the judge-facing `POST /run` endpoint.

    `sample_mode` is REQUIRED and explicit: the caller must declare whether it
    wants the credential-free fixture pipeline (true) or the live path (false).
    The server never silently overrides or falls back between modes.
    """

    question: str
    invoice_id: str
    sample_mode: bool  # required — no implicit default


class RejectedHypothesis(BaseModel):
    id: HypothesisId
    reason: str


class RunResponse(BaseModel):
    """Conceptual response contract for the future `POST /run` endpoint.

    `supported_cause` / `rejected_hypotheses` / `revenue_at_risk` /
    `recommendation` must be DERIVED at runtime from evidence (AGENTS.md §2.8);
    this schema does not fix any value.
    """

    case_id: str
    revenue_at_risk: int
    supported_cause: str
    blocker_class: Optional[BlockerClass] = None
    rejected_hypotheses: list[RejectedHypothesis] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    recommendation: str
    approval_status: ApprovalStatus = "pending"
    trace: list[TraceEntry] = Field(default_factory=list)


class CaseState(BaseModel):
    """Shared investigation case object (ARCHITECTURE.md §3b).

    Operational state only — never hidden reasoning / chain-of-thought.
    """

    case_id: str
    question: str
    invoice_id: str
    contract_id: Optional[str] = None
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    retries: int = 0
    supported_cause: Optional[str] = None
    rejected_hypotheses: list[RejectedHypothesis] = Field(default_factory=list)
    recommendation: Optional[str] = None
    approval_status: ApprovalStatus = "not_required"
    trace: list[TraceEntry] = Field(default_factory=list)
