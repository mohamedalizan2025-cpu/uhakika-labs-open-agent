import { useState } from "react";
import { ChevronDown, Workflow } from "lucide-react";
import type { RunResponse } from "@/types";
import { formatClock, formatConfidence } from "@/lib/format";
import { Card, CardHeader } from "./primitives";

export function TracePanel({ response }: { response: RunResponse }) {
  const [open, setOpen] = useState(false);
  const entries = response.trace;

  return (
    <Card>
      <CardHeader
        title="Trace"
        icon={<Workflow className="h-4 w-4" />}
        hint="operational actions — never model reasoning"
        action={
          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            aria-expanded={open}
            className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium text-slate-300 ring-1 ring-inset ring-slate-700 transition hover:bg-slate-800"
          >
            <ChevronDown className={"h-3.5 w-3.5 transition " + (open ? "rotate-180" : "")} />
            {open ? "Collapse" : "Expand"}
          </button>
        }
      />
      {open ? (
        entries.length === 0 ? (
          <p className="px-5 py-6 text-sm text-slate-400">No trace recorded.</p>
        ) : (
          <ol className="space-y-3 p-4">
            {entries.map((entry, index) => {
              const confidence = formatConfidence(entry.confidence);
              return (
                <li
                  key={`${entry.ts}-${index}`}
                  className="rounded-lg border border-slate-800 bg-slate-950/40 p-3 text-xs"
                >
                  <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
                    <span className="font-semibold text-slate-200">{entry.agent}</span>
                    <span className="text-slate-500">·</span>
                    <span className="font-mono text-slate-400">{entry.action}</span>
                    {entry.tool ? (
                      <span className="rounded bg-slate-800 px-1.5 py-0.5 font-mono text-[10px] text-slate-400">
                        {entry.tool}
                      </span>
                    ) : null}
                    <span className="ml-auto font-mono text-[10px] text-slate-500">
                      {formatClock(entry.ts)}
                    </span>
                  </div>
                  {entry.decision ? (
                    <p className="mt-1.5 text-slate-300">{entry.decision}</p>
                  ) : null}
                  {entry.source_result_summary ? (
                    <p className="mt-1 text-slate-400">{entry.source_result_summary}</p>
                  ) : null}
                  <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-[10px] text-slate-500">
                    <span>model route: <span className="text-slate-400">{entry.model_route ?? "none (sample)"}</span></span>
                    {confidence ? <span>confidence: <span className="text-slate-400">{confidence}</span></span> : null}
                    {entry.retry_count > 0 ? <span>retry: <span className="text-slate-400">{entry.retry_count}</span></span> : null}
                    {entry.evidence_ids.length > 0 ? (
                      <span className="font-mono">
                        {entry.evidence_ids.slice(0, 6).join(", ")}
                        {entry.evidence_ids.length > 6 ? ` +${entry.evidence_ids.length - 6}` : ""}
                      </span>
                    ) : null}
                  </div>
                </li>
              );
            })}
          </ol>
        )
      ) : null}
    </Card>
  );
}
