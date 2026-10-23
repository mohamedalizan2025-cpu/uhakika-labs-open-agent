import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";

import { fetchHealth, runInvestigation, ApiError } from "@/api";
import type { RunRequest, RunResponse } from "@/types";
import { TopBar, type BackendStatus } from "@/components/TopBar";
import { Composer } from "@/components/Composer";
import { CaseSummary } from "@/components/CaseSummary";
import { HypothesisBoard } from "@/components/HypothesisBoard";
import { EvidencePanel } from "@/components/EvidencePanel";
import { RecommendationPanel } from "@/components/RecommendationPanel";
import { TracePanel } from "@/components/TracePanel";
import { EmptyState, ErrorState, LoadingState } from "@/components/WorkspaceStates";

export default function App() {
  const health = useQuery({
    queryKey: ["health"],
    queryFn: ({ signal }) => fetchHealth(signal),
    refetchInterval: 10000,
  });

  const status: BackendStatus = health.isPending
    ? "checking"
    : health.isError
      ? "offline"
      : "online";

  const [invoiceId, setInvoiceId] = useState<string>("");

  const run = useMutation<RunResponse, Error, RunRequest>({
    mutationFn: (request) => runInvestigation(request),
    onSuccess: (_data, request) => setInvoiceId(request.invoice_id),
  });

  const result = run.data;

  // Auto-run the hero scenario once on first load (UX, not hardcoded output).
  const autoRan = useRef(false);
  useEffect(() => {
    if (status === "online" && !autoRan.current) {
      autoRan.current = true;
      const timer = setTimeout(() => {
        run.mutate({
          question: "Why hasn't our TZS 126,000,000 invoice been paid?",
          invoice_id: "INV-004",
        });
      }, 800); // brief settle so the page renders before the stepper animates
      return () => clearTimeout(timer);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <TopBar status={status} />

      <main className="mx-auto max-w-7xl px-5 py-6">
        <Composer
          loading={run.isPending}
          disabled={status === "offline"}
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
          Uhakika V0 · evidence grounded via Zetaris · conclusions derived at
          runtime · sample mode is not sponsor proof.
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
