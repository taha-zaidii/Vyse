import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export type Severity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export const SEVERITY_CLASS: Record<Severity, string> = {
  LOW: "text-sev-low",
  MEDIUM: "text-sev-medium",
  HIGH: "text-sev-high",
  CRITICAL: "text-sev-critical",
};

export const SEVERITY_BG: Record<Severity, string> = {
  LOW: "bg-sev-low/15 text-sev-low border-sev-low/40",
  MEDIUM: "bg-sev-medium/15 text-sev-medium border-sev-medium/40",
  HIGH: "bg-sev-high/15 text-sev-high border-sev-high/40",
  CRITICAL: "bg-sev-critical/15 text-sev-critical border-sev-critical/40",
};

export function formatTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

export function relativeTime(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const s = Math.floor(diffMs / 1000);
  if (s < 60) return `${s}s ago`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24);
  return `${d}d ago`;
}
