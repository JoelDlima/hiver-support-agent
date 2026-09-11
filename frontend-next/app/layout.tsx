import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Hiver — VirginTrains Support Agent",
  description: "Brand-aware support triage: classify, grounded draft, escalate — live technicals.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen">{children}</body>
    </html>
  );
}
