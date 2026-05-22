export default function SettingsPage() {
  return (
    <div className="container py-8 space-y-6">
      <header>
        <div className="text-[11px] uppercase tracking-[0.18em] text-muted-foreground">
          Settings
        </div>
        <h1 className="text-3xl font-semibold tracking-tight">System Configuration</h1>
      </header>

      <section className="rounded-lg border border-dashed border-border bg-card/30 p-8 text-center text-sm text-muted-foreground">
        Cameras, channels, retention, thresholds — UI lands in Phase 4. For now, edit
        <code className="font-mono text-xs mx-1">config/settings.yaml</code> and restart.
      </section>
    </div>
  );
}
