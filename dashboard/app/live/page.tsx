import { LiveFeedGrid } from "@/components/live-feed-grid";

export default function LivePage() {
  return (
    <div className="container py-8 space-y-6">
      <header>
        <div className="text-[11px] uppercase tracking-[0.18em] text-muted-foreground">
          Live Monitoring
        </div>
        <h1 className="text-3xl font-semibold tracking-tight">All Cameras</h1>
      </header>
      <LiveFeedGrid />
    </div>
  );
}
