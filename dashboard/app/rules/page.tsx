export default function RulesPage() {
  return (
    <div className="container py-8 space-y-6">
      <header>
        <div className="text-[11px] uppercase tracking-[0.18em] text-muted-foreground">
          Configuration
        </div>
        <h1 className="text-3xl font-semibold tracking-tight">Rules & Zones</h1>
        <p className="mt-1 text-sm text-muted-foreground max-w-prose">
          Edit temporal rules (the engine that turns noisy detections into trustworthy incidents)
          and draw zone polygons directly on a paused frame from each camera. v1 ships read-only
          — edits land in the YAML files under <code className="font-mono text-xs">config/</code>.
        </p>
      </header>

      <section className="rounded-lg border border-dashed border-border bg-card/30 p-8 text-center text-sm text-muted-foreground">
        Visual YAML editor + polygon drawer arrives in Phase 4 (see PRD §15).
      </section>
    </div>
  );
}
