"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { AlertOctagon, Cctv, Cog, LayoutDashboard, ListChecks, Sliders, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/", label: "Overview", icon: LayoutDashboard },
  { href: "/live", label: "Live Feeds", icon: Cctv },
  { href: "/incidents", label: "Incidents", icon: AlertOctagon },
  { href: "/analytics", label: "Analytics", icon: TrendingUp },
  { href: "/rules", label: "Rules & Zones", icon: Sliders },
  { href: "/settings", label: "Settings", icon: Cog },
];

export function SidebarNav() {
  const pathname = usePathname();
  return (
    <aside className="hidden md:flex w-60 shrink-0 flex-col border-r border-border bg-card/40 backdrop-blur-sm">
      <div className="flex items-center gap-2 px-5 py-5 border-b border-border">
        <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary/20 text-primary">
          <svg viewBox="0 0 24 24" className="h-4 w-4 fill-current">
            <path d="M12 2 22 8v8l-10 6L2 16V8l10-6Z" />
          </svg>
        </div>
        <div>
          <div className="text-sm font-semibold tracking-tight">Vyse</div>
          <div className="text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
            Safety Intelligence
          </div>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = href === "/" ? pathname === "/" : pathname?.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                active
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground",
              )}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="px-5 py-4 border-t border-border text-[11px] text-muted-foreground">
        <div className="flex items-center gap-2">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-sev-low opacity-75" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-sev-low" />
          </span>
          <span>System operational</span>
        </div>
        <div className="mt-1 font-mono">v0.1.0 · localhost:8000</div>
      </div>
    </aside>
  );
}
