import type { ReactNode } from "react";

export function Panel({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return <article className={`rounded-lg border border-line-700 bg-panel-875/90 shadow-panel ${className}`}>{children}</article>;
}
