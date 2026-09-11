"use client";

import * as React from "react";
import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";
import { Inbox, Menu, X } from "lucide-react";
import { ThemeToggle } from "@/components/sg/theme-toggle";
import { cn } from "@/lib/cn";

const NAV_LINKS = [
  { label: "Triage", href: "#triage" },
  { label: "Proof", href: "#proof" },
  { label: "Eval", href: "#eval" },
];

export function SiteHeader() {
  const [scrolled, setScrolled] = React.useState(false);
  const [open, setOpen] = React.useState(false);

  React.useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={cn(
        "site-header sticky top-0 z-40 h-[52px] border-b border-hairline bg-paper/80 backdrop-blur-[20px] backdrop-saturate-[180%]",
        scrolled && "compact"
      )}
    >
      <div className="mx-auto flex h-full max-w-6xl items-center justify-between gap-4 px-4">
        <Link href="/" className="flex items-center gap-2.5" aria-label="Hiver home">
          <span className="flex size-8 items-center justify-center rounded-lg bg-teal text-white">
            <Inbox className="size-4" />
          </span>
          <span className="font-display text-lg font-bold tracking-tight">
            Hiver
          </span>
        </Link>

        <nav className="hidden items-center gap-1 md:flex" aria-label="Primary">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.label}
              href={link.href}
              className="rounded-[12px] px-3 py-1.5 text-sm font-medium text-muted transition-colors hover:text-ink"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <ThemeToggle />
          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            aria-label={open ? "Close menu" : "Open menu"}
            aria-expanded={open}
            className="inline-flex size-9 cursor-pointer items-center justify-center rounded-[12px] border border-hairline bg-card text-ink hover:border-hairline-strong md:hidden"
          >
            {open ? <X className="size-4" /> : <Menu className="size-4" />}
          </button>
        </div>
      </div>

      <AnimatePresence>
        {open && (
          <motion.nav
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ type: "spring", stiffness: 400, damping: 30 }}
            aria-label="Mobile"
            className="border-b border-hairline bg-paper px-4 pt-2 pb-4 md:hidden"
          >
            <div className="flex flex-col gap-1">
              {NAV_LINKS.map((link) => (
                <Link
                  key={link.label}
                  href={link.href}
                  onClick={() => setOpen(false)}
                  className="rounded-[12px] px-3 py-2 text-sm font-medium text-ink transition-colors hover:bg-ink/5"
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </motion.nav>
        )}
      </AnimatePresence>
    </header>
  );
}
