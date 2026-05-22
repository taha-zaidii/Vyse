import type { Metadata } from "next";
import "@/styles/globals.css";
import { Inter, JetBrains_Mono } from "next/font/google";
import { cn } from "@/lib/utils";
import { SidebarNav } from "@/components/sidebar-nav";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans", display: "swap" });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono", display: "swap" });

export const metadata: Metadata = {
  title: "Vyse — AI Workplace Safety Intelligence",
  description:
    "Real-time PPE compliance, drowsiness detection, and incident intelligence for industrial workplaces.",
  icons: { icon: "/favicon.svg" },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={cn("min-h-screen bg-background font-sans", inter.variable, mono.variable)}>
        <div className="flex min-h-screen">
          <SidebarNav />
          <main className="flex-1 overflow-x-hidden">{children}</main>
        </div>
      </body>
    </html>
  );
}
