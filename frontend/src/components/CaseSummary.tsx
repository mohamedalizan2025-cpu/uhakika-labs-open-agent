import { Coins, FileText } from "lucide-react";
import type { RunResponse } from "@/types";
import { BLOCKER_LABELS, INSUFFICIENT_MARKER } from "@/lib/catalog";
import { formatTzs } from "@/lib/format";
import { Card } from "./primitives";

export function CaseSummary({
  response,
  invoiceId,
}: {
  response: RunResponse;
  invoiceId: string;
}) {
  const insufficient = response.supported_cause === INSUFFICIENT_MARKER;

  return (
    <Card className="overflow-hidden">
      <div className="grid gap-px bg-slate-800 sm:grid-cols-[1.3fr_1fr]">
        <div className="bg-slate-900/60 p-5">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <FileText className="h-3.5 w-3.5" />
            <span className="font-mono">{invoiceId}</span>
            <span aria-hidden>·</span>
            <span className="font-mono text-slate-500">case {response.case_id}</span>
          </div>
          <p className="mt-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
            Supported cause
          </p>
          <p
            className={
              "mt-1 text-lg font-semibold " +
              (insufficient ? "text-amber-300" : "text-emerald-300")
            }
          >
            {insufficient ? "Insufficient evidence" : response.supported_cause}
          </p>
          {response.blocker_class ? (
            <p className="mt-1 text-sm text-slate-400">
              Blocker class:{" "}
              <span className="text-slate-200">
                {BLOCKER_LABELS[response.blocker_class]}
              </span>
            </p>
          ) : null}
        </div>

        <div className="flex flex-col justify-center bg-gradient-to-br from-slate-900/60 to-slate-900/30 p-5">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
            <Coins className="h-4 w-4 text-amber-300" />
            Revenue at risk
          </div>
          <p
            className={
              "mt-2 font-mono text-2xl font-semibold tabular-nums " +
              (response.revenue_at_risk > 0 ? "text-rose-200" : "text-slate-300")
            }
          >
            {formatTzs(response.revenue_at_risk)}
          </p>
          {/* Relative exposure gauge */}
          {response.revenue_at_risk > 0 && (
            <div className="mt-3 space-y-1">
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-800">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-rose-500/70 to-rose-400 transition-all duration-500"
                  style={{
                    width: `${Math.min((response.revenue_at_risk / 200_000_000) * 100, 100).toFixed(1)}%`,
                  }}
                />
              </div>
              <p className="text-[10px] text-slate-500">relative exposure</p>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}
