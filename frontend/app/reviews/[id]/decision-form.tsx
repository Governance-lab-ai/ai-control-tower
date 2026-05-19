"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { decideReview } from "@/lib/api";
import type { HumanReviewDecision, HumanReviewStatus } from "@/lib/types";

const decisions: Array<{ value: HumanReviewDecision; label: string; className: string }> = [
  { value: "approved", label: "Approve", className: "border-emerald-400/45 bg-emerald-500/15 text-emerald-100 hover:bg-emerald-500/25" },
  { value: "rejected", label: "Reject", className: "border-red-400/55 bg-red-500/20 text-red-100 hover:bg-red-500/30" },
  { value: "escalated", label: "Escalate", className: "border-rose-400/55 bg-rose-500/20 text-rose-100 hover:bg-rose-500/30" },
];

export function DecisionForm({ reviewId, status }: { reviewId: string; status: HumanReviewStatus }) {
  const router = useRouter();
  const [reviewerId, setReviewerId] = useState("local-reviewer");
  const [reviewerName, setReviewerName] = useState("Local Reviewer");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pendingDecision, setPendingDecision] = useState<HumanReviewDecision | null>(null);

  async function submitDecision(decision: HumanReviewDecision) {
    setError(null);
    setPendingDecision(decision);
    try {
      await decideReview(reviewId, {
        decision,
        reviewer_id: reviewerId.trim(),
        reviewer_name: reviewerName.trim(),
        notes: notes.trim(),
      });
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to submit review decision.");
    } finally {
      setPendingDecision(null);
    }
  }

  if (status !== "pending") {
    return <p className="mt-4 rounded-lg border border-line-700 bg-navy-900 p-4 text-sm text-[#A8B8CA]">This review has already been decided.</p>;
  }

  const disabled = !reviewerId.trim() || !reviewerName.trim() || !notes.trim() || pendingDecision !== null;

  return (
    <div className="mt-5 space-y-4">
      <div className="grid gap-3 md:grid-cols-2">
        <label>
          <span className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">Reviewer ID</span>
          <input
            value={reviewerId}
            onChange={(event) => setReviewerId(event.target.value)}
            className="mt-2 w-full rounded-lg border border-line-700 bg-navy-900 px-3 py-2 text-sm text-[#E6EEF8] outline-none focus:border-trust-teal"
          />
        </label>
        <label>
          <span className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">Reviewer Name</span>
          <input
            value={reviewerName}
            onChange={(event) => setReviewerName(event.target.value)}
            className="mt-2 w-full rounded-lg border border-line-700 bg-navy-900 px-3 py-2 text-sm text-[#E6EEF8] outline-none focus:border-trust-teal"
          />
        </label>
      </div>
      <label>
        <span className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">Decision Notes</span>
        <textarea
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
          className="mt-2 min-h-32 w-full rounded-lg border border-line-700 bg-navy-900 px-3 py-2 text-sm text-[#E6EEF8] outline-none focus:border-trust-teal"
          placeholder="Record the evidence reviewed and the reason for the decision."
        />
      </label>
      {error ? <p className="rounded-lg border border-red-400/50 bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}
      <div className="flex flex-wrap gap-3">
        {decisions.map((decision) => (
          <button
            key={decision.value}
            type="button"
            disabled={disabled}
            onClick={() => submitDecision(decision.value)}
            className={`rounded-lg border px-4 py-2.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-50 ${decision.className}`}
          >
            {pendingDecision === decision.value ? "Saving..." : decision.label}
          </button>
        ))}
      </div>
    </div>
  );
}
