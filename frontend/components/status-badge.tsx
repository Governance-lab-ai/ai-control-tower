type StatusBadgeProps = {
  label: string;
  tone: "trust" | "warning" | "critical" | "neutral";
};

const toneClasses: Record<StatusBadgeProps["tone"], string> = {
  trust: "border-emerald-400/45 bg-emerald-500/15 text-emerald-200",
  warning: "border-amber-400/50 bg-amber-500/15 text-amber-200",
  critical: "border-red-400/60 bg-red-500/20 text-red-200",
  neutral: "border-slate-400/40 bg-slate-500/15 text-slate-200",
};

export function StatusBadge({ label, tone }: StatusBadgeProps) {
  return (
    <span className={`inline-flex items-center rounded-md border px-2 py-1 text-xs font-semibold ${toneClasses[tone]}`}>
      {label}
    </span>
  );
}
