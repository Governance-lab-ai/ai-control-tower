import { Activity, AlertTriangle, ClipboardCheck, Database, FileClock, Gauge, Settings } from "lucide-react";

export function getNavItems(activeLabel: string) {
  return [
    { label: "Dashboard", href: "/", icon: Gauge, active: activeLabel === "Dashboard" },
    { label: "AI Systems", href: "/systems", icon: Database, active: activeLabel === "AI Systems" },
    { label: "Runs", href: "#", icon: Activity, active: activeLabel === "Runs" },
    { label: "Reviews", href: "#", icon: ClipboardCheck, active: activeLabel === "Reviews" },
    { label: "Incidents", href: "#", icon: AlertTriangle, active: activeLabel === "Incidents" },
    { label: "Audit", href: "#", icon: FileClock, active: activeLabel === "Audit" },
    { label: "Settings", href: "#", icon: Settings, active: activeLabel === "Settings" },
  ];
}
