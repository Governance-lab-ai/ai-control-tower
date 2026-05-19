import type { AISystem, AISystemCreate, ApprovalStatus } from "@/lib/types";

const PUBLIC_API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const SERVER_API_BASE_URL = process.env.NEXT_PRIVATE_API_BASE_URL ?? PUBLIC_API_BASE_URL;

function apiBaseUrl(): string {
  return typeof window === "undefined" ? SERVER_API_BASE_URL : PUBLIC_API_BASE_URL;
}

export class ApiError extends Error {
  status: number;
  details: unknown;

  constructor(message: string, status: number, details: unknown = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${apiBaseUrl()}${path}`, {
    ...init,
    headers,
  });

  if (!response.ok) {
    let details: unknown = null;
    try {
      details = await response.json();
    } catch {
      details = await response.text();
    }
    throw new ApiError(`API request failed: ${path}`, response.status, details);
  }

  return response.json();
}

export async function getSystems(): Promise<AISystem[]> {
  return apiFetch<AISystem[]>("/ai-systems", { cache: "no-store" });
}

export async function getSystem(id: string): Promise<AISystem> {
  return apiFetch<AISystem>(`/ai-systems/${id}`, { cache: "no-store" });
}

export async function createSystem(payload: AISystemCreate): Promise<AISystem> {
  return apiFetch<AISystem>("/ai-systems", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateApprovalStatus(id: string, approvalStatus: ApprovalStatus): Promise<AISystem> {
  return apiFetch<AISystem>(`/ai-systems/${id}/approval-status`, {
    method: "PATCH",
    body: JSON.stringify({ approval_status: approvalStatus }),
  });
}
