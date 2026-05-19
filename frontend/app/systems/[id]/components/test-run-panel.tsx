"use client";

import { FormEvent, useState } from "react";

import { ApprovalBadge } from "@/components/registry-badges";
import { Button } from "@/components/ui/button";
import { TextareaField, TextField } from "@/components/ui/form-fields";
import { Panel } from "@/components/ui/panel";
import { runGovernanceGateway } from "@/lib/api";
import type { ApprovalStatus, GovernanceRunResponse, GovernanceRunStatus } from "@/lib/types";

const statusTone: Record<GovernanceRunStatus, string> = {
  executed: "text-emerald-200",
  blocked: "text-rose-200",
  requires_review: "text-amber-200",
  failed: "text-red-200",
};

export function TestRunPanel({
  systemId,
  approvalStatus,
}: {
  systemId: string;
  approvalStatus: ApprovalStatus;
}) {
  const [actor, setActor] = useState("local_mock:governance_admin");
  const [prompt, setPrompt] = useState("Summarise the request using approved policy language.");
  const [inputText, setInputText] = useState("Synthetic support ticket asks for a delivery status update.");
  const [result, setResult] = useState<GovernanceRunResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsRunning(true);
    setError(null);
    setResult(null);

    try {
      const response = await runGovernanceGateway({
        ai_system_id: systemId,
        actor,
        prompt,
        input_text: inputText,
        metadata: { source: "system_detail_test_run" },
      });
      setResult(response);
    } catch {
      setError("Gateway request failed.");
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <Panel className="p-5 md:col-span-12">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <h2 className="text-base font-semibold text-[#E6EEF8]">Test Run</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-[#A8B8CA]">
            Submit a synthetic request through the governance gateway and inspect whether it executes, blocks, or requires review.
          </p>
        </div>
        <ApprovalBadge status={approvalStatus} />
      </div>

      <form onSubmit={handleSubmit} className="mt-5 grid gap-4 md:grid-cols-2">
        <TextField label="Actor" value={actor} onChange={(event) => setActor(event.target.value)} required />
        <TextField label="Prompt" value={prompt} onChange={(event) => setPrompt(event.target.value)} required />
        <TextareaField
          label="Input text"
          value={inputText}
          onChange={(event) => setInputText(event.target.value)}
          required
          className="md:col-span-2"
        />
        <div className="flex justify-end md:col-span-2">
          <Button type="submit" disabled={isRunning}>
            {isRunning ? "Running..." : "Run Through Gateway"}
          </Button>
        </div>
      </form>

      {error ? <p className="mt-4 text-sm text-red-200">{error}</p> : null}

      {result ? (
        <div className="mt-5 rounded-lg border border-line-700 bg-navy-900 p-4">
          <div className="flex flex-wrap items-center gap-3">
            <p className="text-xs font-semibold uppercase tracking-[0.04em] text-[#718198]">Gateway status</p>
            <p className={`font-mono text-sm ${statusTone[result.status]}`}>{result.status}</p>
            {result.run_id ? <p className="font-mono text-xs text-[#A8B8CA]">run_id: {result.run_id}</p> : null}
          </div>
          {result.output_text ? <p className="mt-4 text-sm leading-6 text-[#E6EEF8]">{result.output_text}</p> : null}
          <ul className="mt-4 space-y-2 text-sm text-[#A8B8CA]">
            {result.governance_messages.map((message) => (
              <li key={message}>{message}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </Panel>
  );
}
