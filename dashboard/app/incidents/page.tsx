import { listIncidents } from "@/lib/api";
import { IncidentCard } from "@/components/incident-card";

export const dynamic = "force-dynamic";

export default async function IncidentsPage() {
  let items: Awaited<ReturnType<typeof listIncidents>>["items"] = [];
  try {
    const res = await listIncidents({ limit: 100 });
    items = res.items;
  } catch {
    // API not running yet — show empty state
  }

  return (
    <div className="container py-8 space-y-6">
      <header>
        <div className="text-[11px] uppercase tracking-[0.18em] text-muted-foreground">
          Incidents
        </div>
        <h1 className="text-3xl font-semibold tracking-tight">All Incidents</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Press <kbd className="font-mono text-xs">j</kbd>/<kbd className="font-mono text-xs">k</kbd> to navigate ·
          <kbd className="font-mono text-xs ml-1">x</kbd> to acknowledge ·
          <kbd className="font-mono text-xs ml-1">/</kbd> to search
        </p>
      </header>

      <div className="space-y-2">
        {items.length === 0 ? (
          <div className="rounded-md border border-dashed border-border bg-card/30 p-12 text-center text-sm text-muted-foreground">
            No incidents recorded yet. Once the Vision Agent fires, they&apos;ll appear here in real time.
          </div>
        ) : (
          items.map((i) => <IncidentCard key={i.incident_id} incident={i} />)
        )}
      </div>
    </div>
  );
}
