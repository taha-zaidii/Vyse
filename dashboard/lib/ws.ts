"use client";

import { useEffect, useRef, useState } from "react";
import type { Incident } from "@/lib/api";

const WS_BASE =
  process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000";

export function useIncidentStream(): {
  incidents: Incident[];
  connected: boolean;
} {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    let cancelled = false;
    function connect() {
      const ws = new WebSocket(`${WS_BASE}/ws/stream/incidents`);
      wsRef.current = ws;
      ws.onopen = () => !cancelled && setConnected(true);
      ws.onclose = () => {
        if (cancelled) return;
        setConnected(false);
        setTimeout(connect, 2000);
      };
      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === "incident" && msg.data) {
            setIncidents((prev) => [msg.data as Incident, ...prev].slice(0, 100));
          }
        } catch {
          /* ignore non-JSON pings */
        }
      };
    }
    connect();
    return () => {
      cancelled = true;
      wsRef.current?.close();
    };
  }, []);

  return { incidents, connected };
}
