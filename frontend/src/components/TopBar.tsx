import { CircleDot, ShieldCheck, FlaskConical } from "lucide-react";

export type BackendStatus = "online" | "offline" | "checking";

function StatusPill({ status }: { status: BackendStatus }) {
  const map = {
    online: { text: "Service online", dot: "text-emerald-400", ring: "ring-emerald-500/30" },
    offline: { text: "Service offline", dot: "text-rose-400", ring: "ring-rose-500/30" },
    checking: { text: "Checking…", dot: "text-slate-400", ring: "ring-slate-500/30" },
  } as const;
  const s = map[status];
  return (
    <span
      className={
        "inline-flex items-center gap-1.5 rounded-full bg-slate-800/60 px-3 py-1 text-xs font-medium text-slate-300 ring-1 ring-inset " +
        s.ring
      }
    >
      <CircleDot className={"h-3.5 w-3.5 " + s.dot} />
      {s.text}
    </span>
  );
}

export function TopBar({ status }: { status: BackendStatus }) {
  return (
    <header className="sticky top-0 z-10 border-b border-slate-800 bg-slate-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-5 py-3.5">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-500/10 ring-1 ring-inset ring-emerald-500/30">
            <ShieldCheck className="h-5 w-5 text-emerald-400" />
          </div>
          <div className="leading-tight">
            <p className="text-[15px] font-semibold text-slate-100">Uhakika Labs</p>
            <p className="text-xs text-slate-400">
              Institutional Contract Revenue Assurance
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2.5">
          <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-500/10 px-3 py-1 text-xs font-medium text-amber-300 ring-1 ring-inset ring-amber-500/30">
            <FlaskConical className="h-3.5 w-3.5" />
            Sample mode
          </span>
          <StatusPill status={status} />
        </div>
      </div>
    </header>
  );
}
