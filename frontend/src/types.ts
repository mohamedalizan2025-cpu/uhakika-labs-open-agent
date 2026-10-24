// Client-side mirror of the backend Pydantic contract (agent/models.py).
// These types describe the `POST /run` request/response and `GET /health`
// readiness. No field carries a conclusion — every result value is supplied by
// the backend at runtime.

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
  sample_mode: boolean; // REQUIRED — explicit per request, never omitted
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

export interface IntegrationStatus {
  status: string;
  missing: string[];
}

export interface HealthResponse {
  ok: boolean;
  default_mode: "sample" | "live";
  sample_ready: boolean;
  live_ready: boolean;
  integrations: {
    zetaris: IntegrationStatus;
    nightshift: IntegrationStatus;
  };
  missing_env_names: string[];
}
