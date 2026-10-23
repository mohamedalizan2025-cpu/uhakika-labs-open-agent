import { AlertTriangle, Radio, ScanSearch, Telescope } from "lucide-react";
import { Card, Skeleton } from "./primitives";

export function EmptyState() {
  return (
    <Card className="flex min-h-[16rem] flex-col items-center justify-center gap-3 p-10 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-800/70">
        <Telescope className="h-6 w-6 text-slate-400" />
      </div>
      <div>
        <p className="text-sm font-semibold text-slate-200">
          Start an investigation
        </p>
        <p className="mx-auto mt-1 max-w-sm text-sm text-slate-400">
          Ask why a receivable is stuck and provide an invoice ID. The agent
          routes the question, gathers Zetaris evidence, and explains the
          supported cause with cited records.
        </p>
      </div>
    </Card>
  );
}

const STAGES = [
  "Routing intent",
  "Framing hypotheses",
  "Retrieving Zetaris evidence",
  "Evaluating causes",
  "Drafting recommendation",
];

export function LoadingState() {
  return (
    <div className="space-y-4">
      <Card className="p-5">
        <div className="flex items-center gap-2 text-sm font-medium text-slate-200">
          <Radio className="h-4 w-4 animate-uhakika-pulse text-emerald-400" />
          Agent running — sample pipeline
        </div>
        <ol className="mt-4 space-y-2">
          {STAGES.map((stage, index) => (
            <li key={stage} className="flex items-center gap-3">
              <span
                className="h-2 w-2 rounded-full bg-emerald-400 animate-uhakika-pulse"
                style={{ animationDelay: `${index * 160}ms` }}
              />
              <span className="text-xs text-slate-400">{stage}</span>
            </li>
          ))}
        </ol>
        <p className="mt-4 text-xs text-slate-500">
          Estimated pipeline stages — the authoritative trace is shown once the
          result returns.
        </p>
      </Card>

      <Card className="space-y-3 p-5">
        <Skeleton className="h-6 w-40" />
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-10 w-full" />
      </Card>
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <Card className="flex min-h-[12rem] flex-col items-center justify-center gap-3 p-8 text-center">
      <div className="flex h-11 w-11 items-center justify-center rounded-full bg-rose-500/10 ring-1 ring-inset ring-rose-500/30">
        {/offline|unreachable|runtime/i.test(message) ? (
          <ScanSearch className="h-5 w-5 text-rose-300" />
        ) : (
          <AlertTriangle className="h-5 w-5 text-rose-300" />
        )}
      </div>
      <div>
        <p className="text-sm font-semibold text-rose-200">
          Investigation unavailable
        </p>
        <p className="mx-auto mt-1 max-w-md text-sm text-slate-400">{message}</p>
      </div>
    </Card>
  );
}
