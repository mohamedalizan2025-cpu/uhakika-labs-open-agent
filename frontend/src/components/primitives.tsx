import type { ReactNode } from "react";

// Small, dependency-free primitives in the shadcn visual idiom (Tailwind +
// Lucide). Kept intentionally minimal and consistent across the workspace.

export function Card({
  className = "",
  children,
}: {
  className?: string;
  children: ReactNode;
}) {
  return (
    <section
      className={
        "rounded-xl border border-slate-800 bg-slate-900/60 shadow-sm shadow-black/20 " +
        className
      }
    >
      {children}
    </section>
  );
}

export function CardHeader({
  title,
  icon,
  hint,
  action,
}: {
  title: string;
  icon?: ReactNode;
  hint?: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="flex items-center justify-between gap-3 border-b border-slate-800 px-5 py-3.5">
      <div className="flex items-center gap-2.5">
        {icon ? <span className="text-slate-400">{icon}</span> : null}
        <h2 className="text-sm font-semibold tracking-wide text-slate-200">
          {title}
        </h2>
        {hint ? (
          <span className="text-xs text-slate-500">{hint}</span>
        ) : null}
      </div>
      {action}
    </div>
  );
}

export function Chip({
  className = "",
  children,
}: {
  className?: string;
  children: ReactNode;
}) {
  return (
    <span
      className={
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium " +
        className
      }
    >
      {children}
    </span>
  );
}

export function Skeleton({ className = "" }: { className?: string }) {
  return (
    <div
      className={"animate-uhakika-pulse rounded-md bg-slate-800/70 " + className}
    />
  );
}
