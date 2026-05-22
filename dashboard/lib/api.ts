import type { Severity } from "@/lib/utils";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface Incident {
  incident_id: string;
  created_at: string;
  camera_id: string;
  zone: string | null;
  incident_type: string;
  severity: Severity;
  rule_id: string;
  confidence_avg: number;
  trigger_event_count: number;
  track_id: number | null;
  frame_snapshot_url: string | null;
  acknowledged: boolean;
  acknowledged_at: string | null;
  metadata: Record<string, unknown>;
}

export interface IncidentListResponse {
  items: Incident[];
  count: number;
}

async function fetchJSON<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    cache: "no-store",
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${await res.text()}`);
  }
  return res.json() as Promise<T>;
}

export async function listIncidents(params?: {
  limit?: number;
  severity_gte?: number;
  acknowledged?: boolean;
}): Promise<IncidentListResponse> {
  const q = new URLSearchParams();
  if (params?.limit) q.set("limit", String(params.limit));
  if (params?.severity_gte) q.set("severity_gte", String(params.severity_gte));
  if (params?.acknowledged !== undefined)
    q.set("acknowledged", String(params.acknowledged));
  const qs = q.toString() ? `?${q}` : "";
  return fetchJSON<IncidentListResponse>(`/api/v1/incidents${qs}`);
}

export async function getIncident(id: string): Promise<Incident> {
  return fetchJSON<Incident>(`/api/v1/incidents/${id}`);
}

export async function acknowledgeIncident(id: string): Promise<void> {
  await fetchJSON(`/api/v1/incidents/${id}/acknowledge`, { method: "POST" });
}

export async function getSummary(): Promise<{
  severity_24h: Record<string, number>;
}> {
  return fetchJSON("/api/v1/analytics/summary");
}

export async function getZones(): Promise<{
  items: { zone: string; severity: number; count: number }[];
}> {
  return fetchJSON("/api/v1/analytics/zones");
}

export async function getTrends(): Promise<{
  hourly: { hour: string; count: number }[];
}> {
  return fetchJSON("/api/v1/analytics/trends");
}
