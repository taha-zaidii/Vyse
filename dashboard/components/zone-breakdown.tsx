"use client";

import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { getZones } from "@/lib/api";

const SEV_LABEL: Record<number, string> = { 1: "LOW", 2: "MEDIUM", 3: "HIGH", 4: "CRITICAL" };

export function ZoneBreakdown() {
  const [data, setData] = useState<{ zone: string; count: number; sev: string }[]>([]);

  useEffect(() => {
    let cancelled = false;
    getZones()
      .then((r) => {
        if (cancelled) return;
        setData(
          r.items.map((row) => ({
            zone: row.zone ?? "—",
            count: row.count,
            sev: SEV_LABEL[row.severity] ?? "?",
          })),
        );
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section className="rounded-lg border border-border bg-card/40 p-4">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-[0.12em] text-muted-foreground">
        Incidents by Zone · Last 7 Days
      </h2>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid stroke="hsl(222 22% 18%)" strokeDasharray="3 3" />
            <XAxis dataKey="zone" tick={{ fill: "hsl(220 9% 65%)", fontSize: 11 }} />
            <YAxis tick={{ fill: "hsl(220 9% 65%)", fontSize: 11 }} />
            <Tooltip
              contentStyle={{
                background: "hsl(222 41% 8%)",
                border: "1px solid hsl(222 22% 18%)",
                fontSize: 12,
              }}
            />
            <Bar dataKey="count" fill="hsl(217 91% 60%)" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
