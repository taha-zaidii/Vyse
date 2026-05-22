"use client";

import { AnimatePresence, motion } from "framer-motion";
import { AlertTriangle } from "lucide-react";
import { useIncidentStream } from "@/lib/ws";

export function CriticalBanner() {
  const { incidents } = useIncidentStream();
  const critical = incidents.find((i) => i.severity === "CRITICAL" && !i.acknowledged);

  return (
    <AnimatePresence>
      {critical && (
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.18 }}
          className="glow-critical animate-pulse-critical flex items-center justify-between rounded-lg border border-sev-critical/60 bg-sev-critical/10 px-5 py-4"
        >
          <div className="flex items-center gap-3">
            <AlertTriangle className="h-5 w-5 text-sev-critical" />
            <div>
              <div className="text-sm font-semibold text-sev-critical">
                CRITICAL · {critical.incident_type}
              </div>
              <div className="text-xs text-muted-foreground font-mono">
                {critical.camera_id} · {critical.zone ?? "—"} · track #{critical.track_id ?? "—"}
              </div>
            </div>
          </div>
          <button className="rounded-md border border-sev-critical/40 px-3 py-1.5 text-xs font-medium text-sev-critical hover:bg-sev-critical/10">
            Acknowledge
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
