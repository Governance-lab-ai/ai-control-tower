import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

type NavItem = {
  label: string;
  icon: LucideIcon;
  active?: boolean;
};

type AppShellProps = {
  navItems: NavItem[];
  children: ReactNode;
};

export function AppShell({ navItems, children }: AppShellProps) {
  return (
    <main className="min-h-screen">
      <div className="flex min-h-screen flex-col md:flex-row">
        <aside className="border-b border-line-700 bg-navy-900/95 md:w-64 md:border-b-0 md:border-r">
          <div className="px-5 py-5">
            <p className="text-xs font-semibold uppercase tracking-[0.04em] text-trust-teal">AI Governance</p>
            <p className="mt-2 text-lg font-semibold leading-tight text-[#E6EEF8]">Control Tower</p>
          </div>
          <nav className="flex gap-2 overflow-x-auto px-3 pb-4 md:flex-col md:overflow-visible">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <a
                  key={item.label}
                  href="#"
                  className={`flex min-w-fit items-center gap-3 rounded-lg border px-3 py-2.5 text-sm transition ${
                    item.active
                      ? "border-trust-teal/50 bg-panel-750 text-[#E6EEF8] shadow-trust"
                      : "border-transparent text-[#A8B8CA] hover:border-line-700 hover:bg-panel-875 hover:text-[#E6EEF8]"
                  }`}
                >
                  <Icon className="h-4 w-4" aria-hidden="true" />
                  <span>{item.label}</span>
                </a>
              );
            })}
          </nav>
          <div className="hidden px-5 py-5 md:block">
            <div className="rounded-lg border border-line-700 bg-panel-875 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">Environment</p>
              <p className="mt-2 font-mono text-sm text-[#E6EEF8]">local</p>
              <p className="mt-2 text-xs leading-5 text-[#A8B8CA]">Synthetic demo data. Azure providers are interface targets only.</p>
            </div>
          </div>
        </aside>

        <section className="flex min-w-0 flex-1 flex-col">
          <header className="flex flex-col gap-3 border-b border-line-700 bg-ink-950/50 px-5 py-4 md:flex-row md:items-center md:justify-between md:px-8">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">Organisation</p>
              <p className="mt-1 text-sm font-medium text-[#E6EEF8]">Acme Corp</p>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm md:flex md:items-center">
              <ContextPill label="Mode" value="Local MVP" />
              <ContextPill label="Range" value="Last 24h" />
              <ContextPill label="API" value="localhost:8000" />
            </div>
          </header>
          {children}
        </section>
      </div>
    </main>
  );
}

function ContextPill({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-line-700 bg-panel-875 px-3 py-2">
      <span className="text-xs text-[#718198]">{label}</span>
      <span className="ml-2 font-mono text-xs text-[#E6EEF8]">{value}</span>
    </div>
  );
}
