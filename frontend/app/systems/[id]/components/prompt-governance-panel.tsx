"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { TextareaField, TextField } from "@/components/ui/form-fields";
import { Panel } from "@/components/ui/panel";
import { activatePromptVersion, approvePromptVersion, createPromptVersion, retirePromptVersion } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import type { PromptVersion, PromptVersionStatus } from "@/lib/types";

const statusTone: Record<PromptVersionStatus, "trust" | "warning" | "neutral" | "rose"> = {
  draft: "neutral",
  approved: "warning",
  active: "trust",
  retired: "rose",
};

export function PromptGovernancePanel({
  systemId,
  promptVersions,
}: {
  systemId: string;
  promptVersions: PromptVersion[];
}) {
  const router = useRouter();
  const [name, setName] = useState("");
  const [version, setVersion] = useState("");
  const [promptText, setPromptText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const activePrompt = promptVersions.find((promptVersion) => promptVersion.status === "active");

  async function refreshAfter(action: () => Promise<unknown>) {
    setError(null);
    try {
      await action();
      router.refresh();
    } catch {
      setError("Prompt governance update failed.");
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setError(null);
    try {
      await createPromptVersion(systemId, {
        name,
        version: version.trim() || null,
        prompt_text: promptText,
        status: "draft",
      });
      setName("");
      setVersion("");
      setPromptText("");
      router.refresh();
    } catch {
      setError("Unable to create prompt version.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <Panel className="md:col-span-12">
      <div className="flex flex-col gap-2 border-b border-line-700 px-5 py-4 md:flex-row md:items-start md:justify-between">
        <div>
          <h2 className="text-base font-semibold text-[#E6EEF8]">Prompt Governance</h2>
          <p className="mt-1 max-w-3xl text-sm leading-6 text-[#A8B8CA]">
            Governed runs must use the active approved prompt exactly. Keep variable request content in input text.
          </p>
        </div>
        {activePrompt ? <StatusBadge label={`Active ${activePrompt.version}`} tone="trust" /> : <StatusBadge label="No active prompt" tone="critical" />}
      </div>

      {error ? <p className="px-5 pt-4 text-sm text-red-200">{error}</p> : null}

      <div className="grid gap-5 p-5 xl:grid-cols-[1fr_420px]">
        <div className="overflow-x-auto rounded-lg border border-line-700">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-navy-900/70 text-xs uppercase tracking-[0.04em] text-[#718198]">
              <tr>
                <th className="px-4 py-3 font-semibold">Version</th>
                <th className="px-4 py-3 font-semibold">Prompt</th>
                <th className="px-4 py-3 font-semibold">Status</th>
                <th className="px-4 py-3 font-semibold">Created</th>
                <th className="px-4 py-3 font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line-700">
              {promptVersions.length === 0 ? (
                <tr>
                  <td className="px-4 py-4 text-[#A8B8CA]" colSpan={5}>
                    No prompt versions recorded.
                  </td>
                </tr>
              ) : (
                promptVersions.map((promptVersion) => (
                  <tr key={promptVersion.id} className="align-top hover:bg-panel-825/60">
                    <td className="px-4 py-4">
                      <p className="font-mono text-xs text-[#E6EEF8]">{promptVersion.version}</p>
                      <p className="mt-1 text-xs text-[#A8B8CA]">{promptVersion.name}</p>
                    </td>
                    <td className="max-w-xl px-4 py-4">
                      <p className="max-h-20 overflow-hidden text-sm leading-6 text-[#D6E0EC]">{promptVersion.prompt_text}</p>
                    </td>
                    <td className="px-4 py-4">
                      <StatusBadge label={promptVersion.status} tone={statusTone[promptVersion.status]} />
                    </td>
                    <td className="px-4 py-4 text-xs text-[#A8B8CA]">{formatDateTime(promptVersion.created_at)}</td>
                    <td className="px-4 py-4">
                      <div className="flex flex-wrap gap-2">
                        {promptVersion.status === "draft" ? (
                          <button
                            className="rounded-md border border-line-700 px-2 py-1 text-xs font-semibold text-signal-cyan hover:border-trust-teal"
                            type="button"
                            onClick={() => refreshAfter(() => approvePromptVersion(promptVersion.id))}
                          >
                            Approve
                          </button>
                        ) : null}
                        {promptVersion.status === "approved" ? (
                          <button
                            className="rounded-md border border-line-700 px-2 py-1 text-xs font-semibold text-emerald-200 hover:border-trust-teal"
                            type="button"
                            onClick={() => refreshAfter(() => activatePromptVersion(promptVersion.id))}
                          >
                            Activate
                          </button>
                        ) : null}
                        {promptVersion.status !== "retired" ? (
                          <button
                            className="rounded-md border border-line-700 px-2 py-1 text-xs font-semibold text-rose-200 hover:border-rose-400"
                            type="button"
                            onClick={() => refreshAfter(() => retirePromptVersion(promptVersion.id))}
                          >
                            Retire
                          </button>
                        ) : null}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <form onSubmit={handleSubmit} className="rounded-lg border border-line-700 bg-navy-900 p-4">
          <h3 className="text-sm font-semibold text-[#E6EEF8]">New Prompt Version</h3>
          <div className="mt-4 grid gap-4">
            <TextField label="Name" value={name} onChange={(event) => setName(event.target.value)} required />
            <TextField label="Version label" value={version} onChange={(event) => setVersion(event.target.value)} placeholder="Auto if blank" />
            <TextareaField label="Approved prompt text" value={promptText} onChange={(event) => setPromptText(event.target.value)} required />
            <Button type="submit" disabled={isSaving}>
              {isSaving ? "Saving..." : "Create Draft"}
            </Button>
          </div>
        </form>
      </div>
    </Panel>
  );
}
