import { CircleDot, ShieldCheck, FlaskConical, Zap } from "lucide-react";

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

function ModeToggle({
  mode,
  liveReady,
  onChange,
}: {
  mode: "sample" | "live";
  liveReady: boolean;
  onChange: (m: "sample" | "live") => void;
}) {
  return (
    <div className="flex items-center rounded-lg bg-slate-800/60 p-0.5 ring-1 ring-inset ring-slate-700">
      <button
        type="button"
        onClick={() => onChange("sample")}
        className={
          "rounded-md px-2.5 py-1 text-xs font-medium transition " +
          (mode === "sample"
            ? "bg-emerald-500/15 text-emerald-300"
            : "text-slate-400 hover:text-slate-200")
        }
      >
        <FlaskConical className="mr-1 inline h-3.5 w-3.5" />
        Sample
      </button>
      <button
        type="button"
        onClick={() => onChange("live")}
        disabled={!liveReady}
        className={
          "rounded-md px-2.5 py-1 text-xs font-medium transition " +
          (mode === "live"
            ? "bg-blue-500/15 text-blue-300"
            : "text-slate-400 hover:text-slate-200") +
          (!liveReady ? " cursor-not-allowed opacity-40" : "")
        }
        title={!liveReady ? "Live mode not configured" : undefined}
      >
        <Zap className="mr-1 inline h-3.5 w-3.5" />
        Live
      </button>
    </div>
  );
}

export function TopBar({
  status,
  liveReady,
  mode,
  onModeChange,
}: {
  status: BackendStatus;
  liveReady: boolean;
  mode: "sample" | "live";
  onModeChange: (m: "sample" | "live") => void;
}) {
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
          <ModeToggle mode={mode} liveReady={liveReady} onChange={onModeChange} />
          <StatusPill status={status} />
        </div>
      </div>
    </header>
  );
}
