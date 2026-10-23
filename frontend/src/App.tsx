import { useQuery } from "@tanstack/react-query";
import { Activity, ShieldCheck } from "lucide-react";

// Minimal Investigation Workspace scaffold (Phase 2 foundation only).
// The real workspace panels, hypothesis tree and trace view arrive in Phase 7.
// For now this proves the React/TS/Vite + Tailwind + TanStack Query + Lucide
// wiring by polling the backend liveness endpoint through the dev proxy.

type HealthResponse = { ok: boolean };

async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch("/health");
  if (!response.ok) {
    throw new Error(`health check failed: ${response.status}`);
  }
  return (await response.json()) as HealthResponse;
}

export default function App() {
  const health = useQuery({
    queryKey: ["health"],
    queryFn: fetchHealth,
    refetchInterval: 5000,
  });

  const status = health.isPending
    ? "checking…"
    : health.isError
      ? "backend offline"
      : "backend online";

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex max-w-3xl flex-col gap-6 px-6 py-12">
        <header className="flex items-center gap-3">
          <ShieldCheck className="h-7 w-7 text-emerald-400" />
          <div>
            <h1 className="text-xl font-semibold">Uhakika</h1>
            <p className="text-sm text-slate-400">
              Institutional Contract Revenue Assurance — Investigation Workspace
            </p>
          </div>
        </header>

        <section className="rounded-lg border border-slate-800 bg-slate-900 p-6">
          <div className="flex items-center gap-2 text-sm font-medium">
            <Activity className="h-4 w-4 text-emerald-400" />
            <span>Status: {status}</span>
          </div>
          <p className="mt-3 text-sm text-slate-400">
            Scaffold only. Investigation features are disabled until the agent
            pipeline and workspace phases are approved.
          </p>
        </section>
      </div>
    </main>
  );
}
