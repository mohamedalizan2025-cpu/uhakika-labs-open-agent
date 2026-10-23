import { useEffect, useState } from "react";
import {
  AlertTriangle,
  Check,
  Radio,
  ScanSearch,
  Telescope,
} from "lucide-react";
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

/* ─── Animated Pipeline Stepper ─── */

const STAGES = [
  "Routing intent",
  "Framing hypotheses",
  "Retrieving Zetaris evidence",
  "Evaluating causes",
  "Drafting recommendation",
];

const STEP_MS = 550; // advance one step every 550 ms

export function LoadingState() {
  const [step, setStep] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setStep((prev) => Math.min(prev + 1, STAGES.length));
    }, STEP_MS);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="space-y-4">
      <Card className="p-6">
        {/* Header */}
        <div className="flex items-center gap-2 text-sm font-medium text-slate-200">
          <Radio className="h-4 w-4 animate-uhakika-pulse text-emerald-400" />
          Agent running — sample pipeline
        </div>

        {/* Stepper */}
        <ol className="mt-5 space-y-0">
          {STAGES.map((stage, i) => {
            const done = i < step;
            const active = i === step;
            return (
              <li
                key={stage}
                className="relative flex items-center gap-3 py-2.5 pl-6"
              >
                {/* Connector line */}
                {i < STAGES.length - 1 && (
                  <span
                    className={
                      "absolute left-[11px] top-[34px] h-[calc(100%-10px)] w-px " +
                      (done ? "bg-emerald-500/50" : "bg-slate-700")
                    }
                  />
                )}
                {/* Circle indicator */}
                <span
                  className={
                    "absolute left-0 flex h-[22px] w-[22px] items-center justify-center rounded-full text-[10px] font-bold transition-colors duration-300 " +
                    (done
                      ? "bg-emerald-500/20 text-emerald-300 ring-1 ring-emerald-500/40"
                      : active
                        ? "bg-emerald-500/10 text-emerald-400 ring-1 ring-emerald-400/50 animate-uhakika-pulse"
                        : "bg-slate-800 text-slate-500 ring-1 ring-slate-700")
                  }
                >
                  {done ? <Check className="h-3 w-3" /> : i + 1}
                </span>
                {/* Label */}
                <span
                  className={
                    "text-sm transition-colors duration-300 " +
                    (done
                      ? "text-slate-300"
                      : active
                        ? "text-emerald-200 font-medium"
                        : "text-slate-500")
                  }
                >
                  {stage}
                </span>
              </li>
            );
          })}
        </ol>

        <p className="mt-4 text-[11px] text-slate-500">
          Estimated pipeline stages — the authoritative trace is shown once the
          result returns.
        </p>
      </Card>

      {/* Skeleton placeholders below the stepper */}
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
