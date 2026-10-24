import { useState, type FormEvent } from "react";
import { Loader2, Search } from "lucide-react";
import type { RunRequest } from "@/types";

// One-click sample scenarios: chip click fills the question + invoice AND
// immediately fires the run. This is a convenience for the demo; the pipeline
// still derives conclusions at runtime from the fixtures.

const SAMPLE_SCENARIOS: { id: string; question: string }[] = [
  { id: "INV-004", question: "Why hasn't our TZS 126,000,000 invoice been paid?" },
  { id: "INV-005", question: "Why is the health-depot delivery invoice INV-005 unpaid?" },
  { id: "INV-006", question: "Everything is delivered and accepted for INV-006 — why is payment stuck?" },
];

export function Composer({
  loading,
  disabled,
  onSubmit,
  mode,
}: {
  loading: boolean;
  disabled: boolean;
  onSubmit: (request: RunRequest) => void;
  mode: "sample" | "live";
}) {
  const [question, setQuestion] = useState(
    "Why hasn't this invoice been paid, and what should we do about it?",
  );
  const [invoiceId, setInvoiceId] = useState("INV-004");

  const canSubmit = question.trim().length > 0 && invoiceId.trim().length > 0 && !loading && !disabled;

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!canSubmit) return;
    onSubmit({ question: question.trim(), invoice_id: invoiceId.trim(), sample_mode: mode === "sample" });
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-sm shadow-black/20"
    >
      <label htmlFor="question" className="block text-xs font-semibold uppercase tracking-wide text-slate-400">
        Investigator question
      </label>
      <textarea
        id="question"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        rows={2}
        className="mt-2 w-full resize-y rounded-lg border border-slate-700 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500"
        placeholder="Ask why a receivable is stuck…"
      />

      <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-end">
        <div className="flex-1">
          <label htmlFor="invoice" className="block text-xs font-semibold uppercase tracking-wide text-slate-400">
            Invoice ID
          </label>
          <input
            id="invoice"
            value={invoiceId}
            onChange={(e) => setInvoiceId(e.target.value)}
            className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950/60 px-3 py-2 font-mono text-sm text-slate-100"
            placeholder="INV-004"
          />
        </div>
        <button
          type="submit"
          disabled={!canSubmit}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-emerald-500 px-4 py-2.5 text-sm font-semibold text-emerald-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
          Run investigation
        </button>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <span className="text-xs text-slate-500">Sample scenarios:</span>
        {SAMPLE_SCENARIOS.map(({ id, question: q }) => (
          <button
            key={id}
            type="button"
            disabled={loading || disabled}
            onClick={() => {
              setQuestion(q);
              setInvoiceId(id);
              onSubmit({ question: q, invoice_id: id, sample_mode: true });
            }}
            className={
              "rounded-md px-2 py-1 font-mono text-xs ring-1 ring-inset transition disabled:cursor-not-allowed disabled:opacity-40 " +
              (invoiceId === id
                ? "bg-emerald-500/15 text-emerald-300 ring-emerald-500/40"
                : "bg-slate-800/50 text-slate-400 ring-slate-700 hover:text-slate-200")
            }
          >
            {id}
          </button>
        ))}
      </div>
      {disabled ? (
        <p className="mt-3 text-xs text-amber-300/90">
          The backend service is offline — start FastAPI (uvicorn agent.main:app) to run an investigation.
        </p>
      ) : null}
    </form>
  );
}
