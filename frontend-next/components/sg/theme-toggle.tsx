"use client";

import * as React from "react";
import { motion } from "framer-motion";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { cn } from "@/lib/cn";

export function ThemeToggle({ className }: { className?: string }) {
  const { resolvedTheme, setTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);
  React.useEffect(() => setMounted(true), []);
  // Pre-mount render must be byte-identical on server and client (hydration):
  // fixed icon + label until the resolved theme is known.
  if (!mounted) {
    return (
      <span
        aria-hidden
        className={cn(
          "inline-flex size-9 items-center justify-center rounded-[12px] border border-hairline bg-card text-ink",
          className
        )}
      >
        <Moon className="size-4" />
      </span>
    );
  }
  const dark = resolvedTheme === "dark";

  return (
    <motion.button
      type="button"
      onClick={() => setTheme(dark ? "light" : "dark")}
      whileTap={{ scale: 0.98 }}
      transition={{ type: "spring", stiffness: 400, damping: 30 }}
      aria-label={dark ? "Switch to light mode" : "Switch to dark mode"}
      className={cn(
        "inline-flex size-9 cursor-pointer items-center justify-center rounded-[12px] border border-hairline bg-card text-ink transition-colors hover:border-hairline-strong hover:bg-paper",
        className
      )}
    >
      {dark ? <Sun className="size-4" /> : <Moon className="size-4" />}
    </motion.button>
  );
}
