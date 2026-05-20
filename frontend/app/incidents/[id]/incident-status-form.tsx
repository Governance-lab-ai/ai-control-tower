"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { updateIncident } from "@/lib/api";
import type { IncidentStatus } from "@/lib/types";

const statuses: IncidentStatus[] = ["open", "under_review", "resolved", "dismissed"];

export function IncidentStatusForm({ incidentId, status }: { incidentId: string; status: IncidentStatus }) {
  const router = useRouter();
  const [nextStatus, setNextStatus] = useState<IncidentStatus>(status);
  const [actor, setActor] = useState("local-reviewer");
  const [notes, setNotes] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    setError(null);
    setIsSaving(true);
    try {
      await updateIncident(incidentId, {
        status: nextStatus,
        actor: actor.trim(),
        notes: notes.trim() || undefined,
      });
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update incident.");
    } finally {
      setIsSaving(false);
    }
  }

  const disabled = isSaving || !actor.trim();

  return (
    <div className="mt-5 space-y-4">
      <label>
        <span className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">Status</span>
        <select
          value={nextStatus}
          onChange={(event) => setNextStatus(event.target.value as IncidentStatus)}
          className="mt-2 w-full rounded-lg border border-line-700 bg-navy-900 px-3 py-2 text-sm text-[#E6EEF8] outline-none focus:border-trust-teal"
        >
          {statuses.map((item) => (
            <option key={item} value={item}>
              {item.replace("_", " ")}
            </option>
          ))}
        </select>
      </label>
      <label>
        <span className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">Actor</span>
        <input
          value={actor}
          onChange={(event) => setActor(event.target.value)}
          className="mt-2 w-full rounded-lg border border-line-700 bg-navy-900 px-3 py-2 text-sm text-[#E6EEF8] outline-none focus:border-trust-teal"
        />
      </label>
      <label>
        <span className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">Notes</span>
        <textarea
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
          className="mt-2 min-h-28 w-full rounded-lg border border-line-700 bg-navy-900 px-3 py-2 text-sm text-[#E6EEF8] outline-none focus:border-trust-teal"
          placeholder="Record why this incident status is changing."
        />
      </label>
      {error ? <p className="rounded-lg border border-red-400/50 bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
      <button
        type="button"
        disabled={disabled}
        onClick={submit}
        className="rounded-lg border border-signal-cyan/50 bg-signal-cyan/10 px-4 py-2.5 text-sm font-semibold text-signal-cyan disabled:cursor-not-allowed disabled:opacity-50"
      >
        {isSaving ? "Saving..." : "Update Incident"}
      </button>
    </div>
  );
}
