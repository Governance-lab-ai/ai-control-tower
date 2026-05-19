"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { updateApprovalStatus } from "@/lib/api";
import { APPROVAL_STATUSES } from "@/lib/domain/ai-systems";
import type { ApprovalStatus } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { SelectField } from "@/components/ui/form-fields";
import { Panel } from "@/components/ui/panel";

export function ApprovalStatusControl({ systemId, currentStatus }: { systemId: string; currentStatus: ApprovalStatus }) {
  const router = useRouter();
  const [status, setStatus] = useState<ApprovalStatus>(currentStatus);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function saveStatus() {
    setIsSaving(true);
    setError(null);
    try {
      await updateApprovalStatus(systemId, status);
      router.refresh();
    } catch {
      setError("Status update failed.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <Panel className="p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">Approval control</p>
      <div className="mt-3 flex flex-col gap-3 sm:flex-row">
        <SelectField
          label="Status"
          value={status}
          onChange={(event) => setStatus(event.target.value as ApprovalStatus)}
          options={APPROVAL_STATUSES}
          hideLabel
        />
        <Button
          type="button"
          onClick={saveStatus}
          disabled={isSaving || status === currentStatus}
          className="self-end px-4 py-2"
        >
          {isSaving ? "Saving..." : "Update status"}
        </Button>
      </div>
      {error ? <p className="mt-3 text-sm text-red-200">{error}</p> : null}
    </Panel>
  );
}
