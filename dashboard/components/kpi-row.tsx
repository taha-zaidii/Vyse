import { getSummary } from "@/lib/api";
import { KpiCard } from "@/components/kpi-card";

export async function KpiRow() {
  let summary: Record<string, number> = {};
  try {
    const data = await getSummary();
    summary = data.severity_24h;
  } catch {
    // API not running yet — show empty state
  }

  const total = Object.values(summary).reduce((a, b) => a + b, 0);

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <KpiCard label="Incidents · 24h" value={total} tone="default" />
      <KpiCard label="CRITICAL" value={summary["4"] ?? 0} tone="critical" />
      <KpiCard label="HIGH" value={summary["3"] ?? 0} tone="high" />
      <KpiCard label="MEDIUM" value={summary["2"] ?? 0} tone="medium" />
    </div>
  );
}
