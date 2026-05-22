"use client";

import { useEffect, useState } from "react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { getTrends } from "@/lib/api";

interface Point {
  hour: string;
  count: number;
}

export function TrendChart() {
  const [data, setData] = useState<Point[]>([]);

  useEffect(() => {
    let cancelled = false;
    getTrends()
      .then((r) => !cancelled && setData(r.hourly))
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section className="rounded-lg border border-border bg-card/40 p-4">
      <div className="mb-3">
        <h2 className="text-sm font-semibold uppercase tracking-[0.12em] text-muted-foreground">
          Incidents · Last 7 Days
        </h2>
      </div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 20, bottom: 0, left: 0 }}>
            <defs>
              <linearGradient id="gradPrimary" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="hsl(217 91% 60%)" stopOpacity={0.6} />
                <stop offset="100%" stopColor="hsl(217 91% 60%)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="hsl(222 22% 18%)" strokeDasharray="3 3" />
            <XAxis dataKey="hour" tick={{ fill: "hsl(220 9% 65%)", fontSize: 11 }} tickFormatter={(v) => v.slice(11, 16)} />
            <YAxis tick={{ fill: "hsl(220 9% 65%)", fontSize: 11 }} />
            <Tooltip
              contentStyle={{
                background: "hsl(222 41% 8%)",
                border: "1px solid hsl(222 22% 18%)",
                fontSize: 12,
              }}
            />
            <Area
              type="monotone"
              dataKey="count"
              stroke="hsl(217 91% 60%)"
              fill="url(#gradPrimary)"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
