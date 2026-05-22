import { cn, relativeTime, SEVERITY_BG, type Severity } from "@/lib/utils";
import type { Incident } from "@/lib/api";

const SEV_BAR: Record<Severity, string> = {
  LOW: "bg-sev-low",
  MEDIUM: "bg-sev-medium",
  HIGH: "bg-sev-high",
  CRITICAL: "bg-sev-critical",
};

export function IncidentCard({ incident }: { incident: Incident }) {
  return (
    <div
      className={cn(
        "group relative flex gap-3 overflow-hidden rounded-md border bg-card/60 p-3 transition-colors hover:bg-card",
        incident.severity === "CRITICAL" ? "border-sev-critical/40" : "border-border",
      )}
    >
      <div className={cn("w-1 rounded-full", SEV_BAR[incident.severity])} />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span
            className={cn(
              "rounded-md border px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-[0.15em]",
              SEVERITY_BG[incident.severity],
            )}
          >
            {incident.severity}
          </span>
          <span className="truncate text-sm font-medium">{incident.incident_type}</span>
        </div>
        <div className="mt-1 flex items-center gap-3 text-[11px] text-muted-foreground font-mono">
          <span>{incident.camera_id}</span>
          {incident.zone && <span>· {incident.zone}</span>}
          {incident.track_id != null && <span>· #{incident.track_id}</span>}
          <span>· {relativeTime(incident.created_at)}</span>
        </div>
      </div>
      <button className="self-center opacity-0 group-hover:opacity-100 transition-opacity rounded-md border border-border px-2 py-1 text-[10px] font-mono uppercase tracking-wider text-muted-foreground hover:text-foreground hover:border-primary">
        Ack
      </button>
    </div>
  );
}
