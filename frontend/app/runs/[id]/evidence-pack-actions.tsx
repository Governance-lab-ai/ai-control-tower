"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { getEvidencePack } from "@/lib/api";

export function EvidencePackActions({ runId }: { runId: string }) {
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function exportEvidencePack() {
    setIsExporting(true);
    setError(null);
    try {
      const evidencePack = await getEvidencePack(runId);
      const blob = new Blob([JSON.stringify(evidencePack, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `evidence-pack-${runId}.json`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch {
      setError("Evidence pack export failed.");
    } finally {
      setIsExporting(false);
    }
  }

  return (
    <div className="flex flex-col items-start gap-2 md:items-end">
      <Button type="button" onClick={exportEvidencePack} disabled={isExporting}>
        {isExporting ? "Exporting..." : "Export Evidence Pack"}
      </Button>
      {error ? <p className="text-xs text-red-200">{error}</p> : null}
    </div>
  );
}
