import { Link2 } from "lucide-react";
import type { RunResponse } from "@/types";
import { Card, CardHeader } from "./primitives";

export function EvidencePanel({ response }: { response: RunResponse }) {
  const count = response.evidence.length;
  return (
    <Card>
      <CardHeader
        title="Evidence"
        icon={<Link2 className="h-4 w-4" />}
        hint={count ? `${count} cited record${count === 1 ? "" : "s"}` : undefined}
      />
      {count === 0 ? (
        <p className="px-5 py-6 text-sm text-slate-400">
          No records were retrieved for this case.
        </p>
      ) : (
        <ul className="max-h-72 space-y-2 overflow-y-auto p-4">
          {response.evidence.map((evidence) => (
            <li
              key={evidence.evidence_id + evidence.source}
              className="rounded-lg border border-slate-800 bg-slate-950/40 p-3"
            >
              <div className="flex items-center justify-between gap-2">
                <span className="font-mono text-xs font-semibold text-emerald-300">
                  {evidence.evidence_id}
                </span>
                <span className="text-[11px] uppercase tracking-wide text-slate-500">
                  {evidence.source}
                </span>
              </div>
              <p className="mt-1.5 text-xs leading-relaxed text-slate-300">
                {evidence.summary}
              </p>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
