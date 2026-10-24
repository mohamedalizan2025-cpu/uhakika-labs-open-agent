import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Play } from "lucide-react";

import { fetchHealth, runInvestigation, ApiError } from "@/api";
import type { HealthResponse, RunRequest, RunResponse } from "@/types";
import { TopBar, type BackendStatus } from "@/components/TopBar";
import { Composer } from "@/components/Composer";
import { CaseSummary } from "@/components/CaseSummary";
import { HypothesisBoard } from "@/components/HypothesisBoard";
import { EvidencePanel } from "@/components/EvidencePanel";
import { RecommendationPanel } from "@/components/RecommendationPanel";
import { TracePanel } from "@/components/TracePanel";
import { EmptyState, ErrorState, LoadingState } from "@/components/WorkspaceStates";

// --- Demo auto-run opt-in via Vite environment variable ---
// Default is FALSE: opening the page must never trigger a request.
// Only when VITE_DEMO_AUTORUN === "true" does INV-004 auto-run (always sample).

type Mode = "sample" | "live";

export default function App() {
  // Read env at render time so vi.stubEnv works in tests
  const demoAutorun = import.meta.env.VITE_DEMO_AUTORUN === "true";
  const health = useQuery<HealthResponse, Error>({
    queryKey: ["health"],
    queryFn: ({ signal }) => fetchHealth(signal),
    refetchInterval: 10000,
  });

  const status: BackendStatus = health.isPending
    ? "checking"
    : health.isError
      ? "offline"
      : "online";

  const liveReady = health.data?.live_ready ?? false;

  const [mode, setMode] = useState<Mode>("sample");
  const [invoiceId, setInvoiceId] = useState<string>("");

  const run = useMutation<RunResponse, Error, RunRequest>({
    mutationFn: (request) => runInvestigation(request),
    onSuccess: (_data, request) => setInvoiceId(request.invoice_id),
  });

  const result = run.data;

  // Auto-run hero scenario ONLY when explicitly opted in via VITE_DEMO_AUTORUN.
  const autoRan = useRef(false);
  useEffect(() => {
    if (demoAutorun && status === "online" && !autoRan.current) {
      autoRan.current = true;
      const timer = setTimeout(() => {
        run.mutate({
          question: "Why hasn't our TZS 126,000,000 invoice been paid?",
          invoice_id: "INV-004",
          sample_mode: true, // ALWAYS sample; never live on auto-run
        });
      }, 800);
      return () => clearTimeout(timer);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status]);

  // Guided-demo button handler (manual opt-in without env var).
  function startGuidedDemo() {
    run.mutate({
      question: "Why hasn't our TZS 126,000,000 invoice been paid?",
      invoice_id: "INV-004",
      sample_mode: true, // guided demo is always sample
    });
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <TopBar status={status} liveReady={liveReady} mode={mode} onModeChange={setMode} />

      <main className="mx-auto max-w-7xl px-5 py-6">
        {/* Guided-demo button (visible only when no result and not loading) */}
        {!run.isPending && !result && (
          <div className="mb-4 flex justify-center">
            <button
              type="button"
              onClick={startGuidedDemo}
              disabled={status === "offline"}
              className="inline-flex items-center gap-2 rounded-lg bg-emerald-600/15 px-4 py-2 text-sm font-medium text-emerald-300 ring-1 ring-inset ring-emerald-500/30 transition hover:bg-emerald-600/25 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <Play className="h-4 w-4" />
              Run guided sample investigation
            </button>
          </div>
        )}

        <Composer
          loading={run.isPending}
          disabled={status === "offline" || (mode === "live" && !liveReady)}
          mode={mode}
          onSubmit={(request) => run.mutate(request)}
        />

        <div className="mt-5">
          {run.isPending ? (
            <LoadingState />
          ) : run.isError ? (
            <ErrorState message={describeError(run.error)} />
          ) : result ? (
            <ResultWorkspace response={result} invoiceId={invoiceId} />
          ) : (
            <EmptyState />
          )}
        </div>
      </main>

      <footer className="mx-auto max-w-7xl px-5 pb-8 pt-2">
        <p className="text-xs text-slate-600">
          Uhakika V0 · evidence via Zetaris sample adapter · conclusions derived
          at runtime · sample mode is not sponsor proof.
        </p>
      </footer>
    </div>
  );
}

function ResultWorkspace({
  response,
  invoiceId,
}: {
  response: RunResponse;
  invoiceId: string;
}) {
  return (
    <div className="grid gap-5 lg:grid-cols-[minmax(0,1.6fr)_minmax(0,1fr)]">
      <div className="space-y-5">
        <CaseSummary response={response} invoiceId={invoiceId} />
        <HypothesisBoard response={response} />
        <RecommendationPanel key={response.case_id} response={response} />
      </div>
      <div className="space-y-5">
        <EvidencePanel response={response} />
        <TracePanel response={response} />
      </div>
    </div>
  );
}

function describeError(error: Error): string {
  if (error instanceof ApiError) {
    return error.message;
  }
  return "Something went wrong while running the investigation.";
}
