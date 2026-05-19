import type { ReactNode } from "react";

export type BadgeTone = "trust" | "warning" | "critical" | "neutral" | "orange" | "rose";

const toneClasses: Record<BadgeTone, string> = {
  trust: "border-emerald-400/45 bg-emerald-500/15 text-emerald-200",
  warning: "border-amber-400/50 bg-amber-500/15 text-amber-200",
  critical: "border-red-400/60 bg-red-500/20 text-red-200",
  neutral: "border-slate-400/40 bg-slate-500/15 text-slate-200",
  orange: "border-orange-400/55 bg-orange-500/15 text-orange-200",
  rose: "border-rose-400/60 bg-rose-500/20 text-rose-200",
};

export function Badge({
  tone,
  children,
  className = "",
}: {
  tone: BadgeTone;
  children: ReactNode;
  className?: string;
}) {
  return (
    <span className={`inline-flex items-center rounded-md border px-2 py-1 text-xs font-semibold ${toneClasses[tone]} ${className}`}>
      {children}
    </span>
  );
}
