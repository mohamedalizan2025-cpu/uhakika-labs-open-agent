// Client-side mirror of the backend Pydantic contract (agent/models.py).
// These types describe the `POST /run` request/response only. No field here
// carries a conclusion — every result value is supplied by the backend at
// runtime (see AGENTS.md no-hardcoded-conclusions rule).

export type HypothesisId = "H1" | "H2" | "H3" | "H4" | "H5";

export type BlockerClass =
  | "supplier_controllable"
  | "execution_documentation"
  | "external_payment";

export type ApprovalStatus =
  | "not_required"
  | "pending"
  | "approved"
  | "rejected";

export interface RunRequest {
  question: string;
  invoice_id: string;
  sample_mode?: boolean;
}

export interface Evidence {
  evidence_id: string;
  source: string;
  summary: string;
}

export interface RejectedHypothesis {
  id: HypothesisId;
  reason: string;
}

export interface TraceEntry {
  ts: string;
  agent: string;
  action: string;
  tool?: string | null;
  source_result_summary?: string | null;
  decision?: string | null;
  confidence?: number | null;
  retry_count: number;
  model_route?: string | null;
  evidence_ids: string[];
}

export interface RunResponse {
  case_id: string;
  revenue_at_risk: number;
  supported_cause: string;
  blocker_class: BlockerClass | null;
  rejected_hypotheses: RejectedHypothesis[];
  evidence: Evidence[];
  recommendation: string;
  approval_status: ApprovalStatus;
  trace: TraceEntry[];
}

export interface HealthResponse {
  ok: boolean;
}
