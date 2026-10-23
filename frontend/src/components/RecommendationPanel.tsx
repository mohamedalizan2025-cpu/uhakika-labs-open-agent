import { useState } from "react";
import { ClipboardCheck, ShieldQuestion, Check, X } from "lucide-react";
import type { RunResponse } from "@/types";
import { Card, CardHeader, Chip } from "./primitives";

export function RecommendationPanel({ response }: { response: RunResponse }) {
  const needsApproval = response.approval_status === "pending";
  const [decision, setDecision] = useState<"pending" | "approved" | "declined">(
    "pending",
  );

  return (
    <Card>
      <CardHeader
        title="Recommendation"
        icon={<ClipboardCheck className="h-4 w-4" />}
        action={
          needsApproval ? (
            <Chip className="bg-amber-500/15 text-amber-300 ring-1 ring-inset ring-amber-500/30">
              <ShieldQuestion className="h-3.5 w-3.5" />
              Human approval required
            </Chip>
          ) : (
            <Chip className="bg-slate-700/40 text-slate-300 ring-1 ring-inset ring-slate-600/50">
              No consequential action
            </Chip>
          )
        }
      />
      <div className="space-y-4 p-5">
        <p className="text-sm leading-relaxed text-slate-200">
          {response.recommendation}
        </p>

        {needsApproval ? (
          <div className="rounded-lg border border-slate-800 bg-slate-950/40 p-4">
            {decision === "pending" ? (
              <div className="flex flex-wrap items-center gap-3">
                <span className="text-xs text-slate-400">
                  Review the evidence, then record an approval decision:
                </span>
                <div className="ml-auto flex gap-2">
                  <button
                    type="button"
                    onClick={() => setDecision("approved")}
                    className="inline-flex items-center gap-1.5 rounded-md bg-emerald-500 px-3 py-1.5 text-xs font-semibold text-emerald-950 transition hover:bg-emerald-400"
                  >
                    <Check className="h-3.5 w-3.5" /> Approve
                  </button>
                  <button
                    type="button"
                    onClick={() => setDecision("declined")}
                    className="inline-flex items-center gap-1.5 rounded-md bg-slate-700 px-3 py-1.5 text-xs font-semibold text-slate-100 transition hover:bg-slate-600"
                  >
                    <X className="h-3.5 w-3.5" /> Decline
                  </button>
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-400">
                Decision recorded locally:{" "}
                <span
                  className={
                    "font-semibold " +
                    (decision === "approved" ? "text-emerald-300" : "text-rose-300")
                  }
                >
                  {decision === "approved" ? "Approved" : "Declined"}
                </span>
                . This V0 workspace is explain-only — it logs your decision but
                performs no external action (ActionAgent is a deferred stretch).
              </p>
            )}
          </div>
        ) : null}
      </div>
    </Card>
  );
}
