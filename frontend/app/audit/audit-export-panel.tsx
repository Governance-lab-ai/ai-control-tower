"use client";

import { useMemo, useState } from "react";
import { Download } from "lucide-react";

import { Button } from "@/components/ui/button";
import { buildAuditExportUrl } from "@/lib/api";
import type { AISystem, RiskLevel } from "@/lib/types";

type ExportFormat = "csv" | "json";

export function AuditExportPanel({ systems }: { systems: AISystem[] }) {
  const [format, setFormat] = useState<ExportFormat>("csv");
  const [systemId, setSystemId] = useState("");
  const [department, setDepartment] = useState("");
  const [riskLevel, setRiskLevel] = useState("");
  const [incidentType, setIncidentType] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const departments = useMemo(() => Array.from(new Set(systems.map((system) => system.department))).sort(), [systems]);
  const selectedSystem = systems.find((system) => system.id === systemId);
  const exportUrl = buildAuditExportUrl({
    format,
    system_id: systemId,
    department: systemId ? "" : department,
    risk_level: riskLevel,
    incident_type: incidentType,
    start_date: startDate ? `${startDate}T00:00:00Z` : "",
    end_date: endDate ? `${endDate}T23:59:59Z` : "",
  });

  return (
    <section className="px-5 pt-5 md:px-8">
      <div className="rounded-lg border border-line-700 bg-panel-875/90 p-5 shadow-panel">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h2 className="text-base font-semibold text-[#E6EEF8]">Audit Export</h2>
            <p className="mt-1 text-sm text-[#A8B8CA]">Generate filtered CSV or JSON evidence from the audit ledger.</p>
          </div>
          <a href={exportUrl} download={`audit-export.${format}`}>
            <Button type="button">
              <Download className="h-4 w-4" aria-hidden="true" />
              Export {format.toUpperCase()}
            </Button>
          </a>
        </div>

        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <label className="flex flex-col gap-2 text-sm">
            <span className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">Format</span>
            <select value={format} onChange={(event) => setFormat(event.target.value as ExportFormat)} className={fieldClass}>
              <option value="csv">CSV</option>
              <option value="json">JSON</option>
            </select>
          </label>

          <label className="flex flex-col gap-2 text-sm">
            <span className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">System</span>
            <select value={systemId} onChange={(event) => setSystemId(event.target.value)} className={fieldClass}>
              <option value="">All systems</option>
              {systems.map((system) => (
                <option key={system.id} value={system.id}>
                  {system.name}
                </option>
              ))}
            </select>
          </label>

          <label className="flex flex-col gap-2 text-sm">
            <span className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">Department</span>
            <select value={department} onChange={(event) => setDepartment(event.target.value)} className={fieldClass} disabled={Boolean(systemId)}>
              <option value="">{selectedSystem ? selectedSystem.department : "All departments"}</option>
              {departments.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <label className="flex flex-col gap-2 text-sm">
            <span className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">Risk</span>
            <select value={riskLevel} onChange={(event) => setRiskLevel(event.target.value as RiskLevel | "")} className={fieldClass}>
              <option value="">All risks</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </label>

          <label className="flex flex-col gap-2 text-sm">
            <span className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">Incident type</span>
            <input
              value={incidentType}
              onChange={(event) => setIncidentType(event.target.value)}
              placeholder="pii_detected_input"
              className={fieldClass}
            />
          </label>

          <label className="flex flex-col gap-2 text-sm">
            <span className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">Start date</span>
            <input type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} className={fieldClass} />
          </label>

          <label className="flex flex-col gap-2 text-sm">
            <span className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">End date</span>
            <input type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} className={fieldClass} />
          </label>
        </div>
      </div>
    </section>
  );
}

const fieldClass =
  "h-10 rounded-lg border border-line-700 bg-navy-900 px-3 text-sm text-[#E6EEF8] outline-none focus:border-trust-teal disabled:cursor-not-allowed disabled:opacity-60";
