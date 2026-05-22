import { Suspense } from "react";
import { TrendChart } from "@/components/trend-chart";
import { ZoneBreakdown } from "@/components/zone-breakdown";

export default function AnalyticsPage() {
  return (
    <div className="container py-8 space-y-6">
      <header>
        <div className="text-[11px] uppercase tracking-[0.18em] text-muted-foreground">
          Analytics
        </div>
        <h1 className="text-3xl font-semibold tracking-tight">Trends & Compliance</h1>
      </header>

      <Suspense fallback={<div className="h-72 animate-pulse rounded-lg bg-muted" />}>
        <TrendChart />
      </Suspense>

      <ZoneBreakdown />
    </div>
  );
}
