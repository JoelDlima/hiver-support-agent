"use client";

type Stage = { name: string; ms?: number; state: "done" | "active" | "idle"; note?: string };

export default function PipelineTimeline({ stages }: { stages: Stage[] }) {
  return (
    <ol className="flex flex-col gap-2">
      {stages.map((s) => (
        <li
          key={s.name}
          className={`flex items-center justify-between rounded-md border px-3 py-2 text-sm ${
            s.state === "active"
              ? "border-cyan-500 bg-cyan-950/40"
              : s.state === "done"
                ? "border-slate-700 bg-slate-900/60"
                : "border-slate-800 text-slate-500"
          }`}
        >
          <span className="font-medium">
            {s.state === "active" ? "● " : s.state === "done" ? "✓ " : "○ "}
            {s.name}
            {s.note ? <span className="ml-2 text-xs text-slate-400">{s.note}</span> : null}
          </span>
          <span className="tabular-nums text-xs text-slate-300">
            {s.ms !== undefined ? `${s.ms} ms` : "—"}
          </span>
        </li>
      ))}
    </ol>
  );
}
