import { Suspense } from "react";
import { KpiRow } from "@/components/kpi-row";
import { IncidentFeedLive } from "@/components/incident-feed-live";
import { LiveFeedGrid } from "@/components/live-feed-grid";
import { TrendChart } from "@/components/trend-chart";
import { CriticalBanner } from "@/components/critical-banner";

export const dynamic = "force-dynamic";

export default function OverviewPage() {
  return (
    <div className="container py-8 space-y-8">
      <header className="flex items-end justify-between">
        <div>
          <div className="text-[11px] uppercase tracking-[0.18em] text-muted-foreground">
            Command Center
          </div>
          <h1 className="text-3xl font-semibold tracking-tight">Today on shift</h1>
        </div>
        <div className="font-mono text-xs text-muted-foreground">
          {new Date().toLocaleString([], { dateStyle: "medium", timeStyle: "short" })}
        </div>
      </header>

      <CriticalBanner />

      <Suspense fallback={<div className="h-28 animate-pulse rounded-lg bg-muted" />}>
        <KpiRow />
      </Suspense>

      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <LiveFeedGrid />
          <Suspense fallback={<div className="h-72 animate-pulse rounded-lg bg-muted" />}>
            <TrendChart />
          </Suspense>
        </div>
        <div>
          <IncidentFeedLive />
        </div>
      </section>
    </div>
  );
}
