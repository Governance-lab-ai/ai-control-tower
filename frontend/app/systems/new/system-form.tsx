"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { createSystem } from "@/lib/api";
import { APPROVAL_STATUSES, RISK_LEVELS, splitCommaList } from "@/lib/domain/ai-systems";
import type { AISystemCreate, ApprovalStatus, RiskLevel } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { CheckboxField, SelectField, TextareaField, TextField } from "@/components/ui/form-fields";
import { Panel } from "@/components/ui/panel";

const emptyForm: AISystemCreate = {
  name: "",
  description: "",
  department: "",
  owner_name: "",
  owner_email: "",
  model_provider: "mock",
  model_name: "",
  data_sources: [],
  contains_personal_data: false,
  risk_level: "medium",
  human_oversight_required: true,
  approval_status: "pending",
};

export function SystemForm() {
  const router = useRouter();
  const [form, setForm] = useState<AISystemCreate>(emptyForm);
  const [dataSources, setDataSources] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setError(null);

    try {
      const created = await createSystem({
        ...form,
        data_sources: splitCommaList(dataSources),
      });
      router.push(`/systems/${created.id}`);
      router.refresh();
    } catch {
      setError("Unable to register system. Check required fields and try again.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <Panel className="p-5">
      <form onSubmit={handleSubmit} className="grid gap-4 md:grid-cols-2">
      <TextField label="System name" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required />
      <TextField label="Department" value={form.department} onChange={(event) => setForm({ ...form, department: event.target.value })} required />
      <TextField label="Owner name" value={form.owner_name} onChange={(event) => setForm({ ...form, owner_name: event.target.value })} required />
      <TextField label="Owner email" type="email" value={form.owner_email} onChange={(event) => setForm({ ...form, owner_email: event.target.value })} required />
      <TextField label="Model provider" value={form.model_provider} onChange={(event) => setForm({ ...form, model_provider: event.target.value })} required />
      <TextField label="Model name" value={form.model_name} onChange={(event) => setForm({ ...form, model_name: event.target.value })} required />
      <SelectField
        label="Risk level"
        value={form.risk_level}
        options={RISK_LEVELS}
        onChange={(event) => setForm({ ...form, risk_level: event.target.value as RiskLevel })}
      />
      <SelectField
        label="Approval status"
        value={form.approval_status}
        options={APPROVAL_STATUSES}
        onChange={(event) => setForm({ ...form, approval_status: event.target.value as ApprovalStatus })}
      />
      <TextareaField
        label="Description"
        value={form.description}
        onChange={(event) => setForm({ ...form, description: event.target.value })}
        required
        className="md:col-span-2"
      />
      <TextField
        label="Data sources, comma separated"
        value={dataSources}
        onChange={(event) => setDataSources(event.target.value)}
        className="md:col-span-2"
      />
      <CheckboxField
        label="Contains personal data"
        checked={form.contains_personal_data}
        onChange={(event) => setForm({ ...form, contains_personal_data: event.target.checked })}
      />
      <CheckboxField
        label="Human oversight required"
        checked={form.human_oversight_required}
        onChange={(event) => setForm({ ...form, human_oversight_required: event.target.checked })}
      />
      {error ? <p className="md:col-span-2 text-sm text-red-200">{error}</p> : null}
      <div className="flex justify-end md:col-span-2">
        <Button
          type="submit"
          disabled={isSaving}
        >
          {isSaving ? "Registering..." : "Register System"}
        </Button>
      </div>
      </form>
    </Panel>
  );
}
