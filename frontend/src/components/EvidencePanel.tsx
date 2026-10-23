import {
  Award,
  Banknote,
  FileText,
  Link2,
  MessageSquare,
  Receipt,
  Shield,
  Truck,
} from "lucide-react";
import type { RunResponse } from "@/types";
import { Card, CardHeader } from "./primitives";

/** Map evidence source to a distinctive Lucide icon. */
function SourceIcon({ source }: { source: string }) {
  const base = "h-3.5 w-3.5 shrink-0";
  switch (source) {
    case "contracts":
      return <FileText className={`${base} text-blue-400`} />;
    case "invoices":
      return <Receipt className={`${base} text-violet-400`} />;
    case "deliveries":
      return <Truck className={`${base} text-cyan-400`} />;
    case "acceptance_records":
      return <Award className={`${base} text-amber-400`} />;
    case "compliance_items":
      return <Shield className={`${base} text-emerald-400`} />;
    case "communications":
      return <MessageSquare className={`${base} text-pink-400`} />;
    case "payment_status":
      return <Banknote className={`${base} text-rose-400`} />;
    default:
      return <FileText className={`${base} text-slate-400`} />;
  }
}

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
              <div className="flex items-center gap-2">
                <SourceIcon source={evidence.source} />
                <span className="font-mono text-xs font-semibold text-emerald-300">
                  {evidence.evidence_id}
                </span>
                <span className="ml-auto text-[11px] uppercase tracking-wide text-slate-500">
                  {evidence.source.replace(/_/g, " ")}
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
