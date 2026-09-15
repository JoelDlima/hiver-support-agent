/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        // Space Grotesk (display) + Inter (sans) + JetBrains Mono (mono) via
        // next/font/google in app/layout.tsx, wired here through CSS variables.
        display: ["var(--font-display)", "system-ui", "-apple-system", "sans-serif"],
        sans: ["var(--font-sans)", "system-ui", "-apple-system", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      colors: {
        paper: "var(--color-paper)",
        ink: "var(--color-ink)",
        muted: "var(--color-muted)",
        hairline: {
          DEFAULT: "var(--color-hairline)",
          soft: "var(--color-hairline-soft)",
          strong: "var(--color-hairline-strong)",
        },
        card: "var(--color-card)",
        raised: "var(--color-raised)",
        teal: "var(--color-teal)",
        aqua: "var(--color-aqua)",
        // Compat aliases for pre-retheme page code.
        canvas: "var(--bg)",
        surface: "var(--surface)",
        line: "var(--border)",
        accent: "var(--accent)",
        success: "var(--success)",
        warning: "var(--warning)",
        danger: "var(--danger)",
      },
    },
  },
  plugins: [],
};
