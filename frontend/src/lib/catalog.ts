import type { BlockerClass, HypothesisId } from "@/types";

// Static hypothesis VOCABULARY only (ids, labels, what each tests) — this mirrors
// the neutral catalog in agent/hypotheses.py. It carries NO conclusions: which
// hypothesis is supported/rejected is decided by the backend and read from the
// `POST /run` response at runtime.

export const INSUFFICIENT_MARKER = "insufficient_evidence";

export interface HypothesisMeta {
  id: HypothesisId;
  label: string;
  tests: string;
}

export const HYPOTHESES: HypothesisMeta[] = [
  { id: "H1", label: "Delivery incomplete", tests: "Are the goods/services fully delivered and evidenced?" },
  { id: "H2", label: "Acceptance certificate missing", tests: "Is there an issued acceptance certificate?" },
  { id: "H3", label: "Invoice submitted late", tests: "Was the invoice submitted after the required date?" },
  { id: "H4", label: "Required compliance / tax evidence missing", tests: "Is a mandatory compliance/tax document outstanding?" },
  { id: "H5", label: "External buyer / payment-stage blockage", tests: "Is payment held by the buyer/treasury for external reasons?" },
];

// Map the backend's `supported_cause` label back to a hypothesis id. The backend
// returns the label string; matching it here is presentation only.
export function hypothesisIdForCause(supportedCause: string): HypothesisId | null {
  const match = HYPOTHESES.find((h) => h.label === supportedCause);
  return match ? match.id : null;
}

export type HypothesisStatus = "supported" | "rejected" | "insufficient";

export interface StatusStyle {
  label: string;
  card: string;
  chip: string;
  dot: string;
}

// Deep, restrained institutional palette: emerald = supported, amber = caution /
// insufficient, slate = rejected / neutral, rose used sparingly for material risk.
export const STATUS_STYLES: Record<HypothesisStatus, StatusStyle> = {
  supported: {
    label: "Supported by evidence",
    card: "border-emerald-500/40 bg-emerald-500/[0.06]",
    chip: "bg-emerald-500/15 text-emerald-300 ring-1 ring-inset ring-emerald-500/30",
    dot: "bg-emerald-400",
  },
  insufficient: {
    label: "Insufficient evidence",
    card: "border-amber-500/40 bg-amber-500/[0.05]",
    chip: "bg-amber-500/15 text-amber-300 ring-1 ring-inset ring-amber-500/30",
    dot: "bg-amber-400",
  },
  rejected: {
    label: "Rejected",
    card: "border-slate-700/70 bg-slate-800/30",
    chip: "bg-slate-700/40 text-slate-300 ring-1 ring-inset ring-slate-600/50",
    dot: "bg-slate-500",
  },
};

export const BLOCKER_LABELS: Record<BlockerClass, string> = {
  supplier_controllable: "Supplier-controllable",
  execution_documentation: "Execution / documentation",
  external_payment: "External / payment-stage",
};
