import { Cctv } from "lucide-react";

const CAMERAS = [
  { id: "cam-1", name: "Floor — Machinery Bay" },
  { id: "cam-2", name: "Control Room" },
];

export function LiveFeedGrid() {
  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-[0.12em] text-muted-foreground">
          Live Feeds
        </h2>
        <a href="/live" className="text-xs text-primary hover:underline">
          Expand all →
        </a>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {CAMERAS.map((cam) => (
          <FeedTile key={cam.id} {...cam} />
        ))}
      </div>
    </section>
  );
}

function FeedTile({ id, name }: { id: string; name: string }) {
  return (
    <div className="group relative overflow-hidden rounded-lg border border-border bg-secondary/40">
      <div className="aspect-video flex items-center justify-center bg-gradient-to-br from-secondary to-card">
        <Cctv className="h-10 w-10 text-muted-foreground/60" />
        <span className="absolute bottom-3 left-3 rounded-md bg-background/70 px-2 py-1 text-[10px] font-mono uppercase tracking-[0.12em] text-muted-foreground backdrop-blur-sm">
          {id} · live · 15 FPS
        </span>
      </div>
      <div className="flex items-center justify-between px-4 py-2 border-t border-border">
        <div className="text-sm">{name}</div>
        <div className="flex items-center gap-1.5 text-[11px] text-sev-low">
          <span className="h-1.5 w-1.5 rounded-full bg-sev-low" />
          OK
        </div>
      </div>
    </div>
  );
}
