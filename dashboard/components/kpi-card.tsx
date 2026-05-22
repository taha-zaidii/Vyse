import { cn } from "@/lib/utils";

type Tone = "default" | "critical" | "high" | "medium" | "low";

const TONE_CLASS: Record<Tone, string> = {
  default: "border-border",
  critical: "border-sev-critical/40 text-sev-critical",
  high: "border-sev-high/40 text-sev-high",
  medium: "border-sev-medium/40 text-sev-medium",
  low: "border-sev-low/40 text-sev-low",
};

export function KpiCard({
  label,
  value,
  tone = "default",
}: {
  label: string;
  value: number | string;
  tone?: Tone;
}) {
  return (
    <div
      className={cn(
        "rounded-lg border bg-card/40 p-4 backdrop-blur-sm",
        TONE_CLASS[tone],
      )}
    >
      <div className="text-[10px] font-mono uppercase tracking-[0.18em] text-muted-foreground">
        {label}
      </div>
      <div className="mt-1 font-sans text-3xl font-semibold tabular-nums">{value}</div>
    </div>
  );
}
