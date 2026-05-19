import type { ReactNode } from "react";

export function PageHeader({
  kicker,
  title,
  description,
  action,
  backLink,
}: {
  kicker?: string;
  title: string;
  description?: string;
  action?: ReactNode;
  backLink?: ReactNode;
}) {
  return (
    <section className="flex flex-col gap-4 border-b border-line-700/80 px-5 py-5 md:flex-row md:items-end md:justify-between md:px-8">
      <div>
        {backLink}
        {kicker ? <p className="text-xs font-semibold uppercase tracking-[0.04em] text-trust-teal">{kicker}</p> : null}
        <h1 className={backLink ? "mt-3 text-2xl font-semibold text-[#E6EEF8] md:text-[28px]" : "mt-2 text-2xl font-semibold text-[#E6EEF8] md:text-[28px]"}>
          {title}
        </h1>
        {description ? <p className="mt-2 max-w-3xl text-sm leading-6 text-[#A8B8CA]">{description}</p> : null}
      </div>
      {action}
    </section>
  );
}
