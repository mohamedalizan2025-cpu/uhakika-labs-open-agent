import { CheckCircle2, MinusCircle, HelpCircle } from "lucide-react";
import type { RunResponse } from "@/types";
import {
  HYPOTHESES,
  STATUS_STYLES,
  hypothesisIdForCause,
  type HypothesisStatus,
} from "@/lib/catalog";
import { Card, CardHeader } from "./primitives";

const ICONS: Record<HypothesisStatus, typeof CheckCircle2> = {
  supported: CheckCircle2,
  rejected: MinusCircle,
  insufficient: HelpCircle,
};

export function HypothesisBoard({ response }: { response: RunResponse }) {
  const supportedId = hypothesisIdForCause(response.supported_cause);
  const rejectedReasons = new Map(
    response.rejected_hypotheses.map((r) => [r.id, r.reason]),
  );

  const statuses = HYPOTHESES.map((hypothesis) => {
    let status: HypothesisStatus;
    if (hypothesis.id === supportedId) status = "supported";
    else if (rejectedReasons.has(hypothesis.id)) status = "rejected";
    else status = "insufficient";
    return { hypothesis, status, reason: rejectedReasons.get(hypothesis.id) };
  });

  return (
    <Card>
      <CardHeader title="Hypotheses" hint="competing causes, evidence-ranked" />
      <ul className="divide-y divide-slate-800">
        {statuses.map(({ hypothesis, status, reason }) => {
          const style = STATUS_STYLES[status];
          const Icon = ICONS[status];
          return (
            <li key={hypothesis.id} className={"m-3 rounded-lg border p-3.5 " + style.card}>
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className={"h-2 w-2 rounded-full " + style.dot} />
                    <span className="font-mono text-xs text-slate-400">{hypothesis.id}</span>
                    <p className="truncate text-sm font-semibold text-slate-100">
                      {hypothesis.label}
                    </p>
                  </div>
                  <p className="mt-1 text-xs text-slate-400">{hypothesis.tests}</p>
                  {reason ? (
                    <p className="mt-2 text-xs text-slate-300">
                      <span className="text-slate-500">Why rejected: </span>
                      {reason}
                    </p>
                  ) : null}
                </div>
                <span
                  className={
                    "inline-flex shrink-0 items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium " +
                    style.chip
                  }
                >
                  <Icon className="h-3.5 w-3.5" />
                  {style.label}
                </span>
              </div>
            </li>
          );
        })}
      </ul>
    </Card>
  );
}
