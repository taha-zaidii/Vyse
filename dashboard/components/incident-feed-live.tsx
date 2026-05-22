"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useIncidentStream } from "@/lib/ws";
import { IncidentCard } from "@/components/incident-card";

export function IncidentFeedLive() {
  const { incidents, connected } = useIncidentStream();

  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-[0.12em] text-muted-foreground">
          Live Incidents
        </h2>
        <span
          className={`text-[10px] font-mono uppercase tracking-[0.15em] ${
            connected ? "text-sev-low" : "text-muted-foreground"
          }`}
        >
          {connected ? "● connected" : "○ offline"}
        </span>
      </div>

      <div className="space-y-2 max-h-[640px] overflow-y-auto pr-1">
        {incidents.length === 0 && (
          <div className="rounded-md border border-dashed border-border bg-card/30 p-8 text-center text-sm text-muted-foreground">
            No incidents yet. The feed updates in real time as Vyse&apos;s agents fire alerts.
          </div>
        )}
        <AnimatePresence initial={false}>
          {incidents.map((incident) => (
            <motion.div
              key={incident.incident_id}
              layout
              initial={{ opacity: 0, x: 24, scale: 0.98 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: -8 }}
              transition={{ type: "spring", stiffness: 280, damping: 30 }}
            >
              <IncidentCard incident={incident} />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </section>
  );
}
