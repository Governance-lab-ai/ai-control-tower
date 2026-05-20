import { Activity, AlertTriangle, BarChart3, ClipboardCheck, Database, FileClock, Gauge, Settings } from "lucide-react";

export function getNavItems(activeLabel: string) {
  return [
    { label: "Dashboard", href: "/", icon: Gauge, active: activeLabel === "Dashboard" },
    { label: "AI Systems", href: "/systems", icon: Database, active: activeLabel === "AI Systems" },
    { label: "Runs", href: "/runs", icon: Activity, active: activeLabel === "Runs" },
    { label: "Evaluations", href: "/evaluations", icon: BarChart3, active: activeLabel === "Evaluations" },
    { label: "Reviews", href: "/reviews", icon: ClipboardCheck, active: activeLabel === "Reviews" },
    { label: "Incidents", href: "/incidents", icon: AlertTriangle, active: activeLabel === "Incidents" },
    { label: "Audit", href: "/audit", icon: FileClock, active: activeLabel === "Audit" },
    { label: "Settings", href: "#", icon: Settings, active: activeLabel === "Settings" },
  ];
}
