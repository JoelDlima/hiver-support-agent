"use client";

type Stage = { name: string; ms?: number; state: "done" | "active" | "idle"; note?: string };

export default function PipelineTimeline({ stages }: { stages: Stage[] }) {
  return (
    <ol className="flex flex-col gap-1.5">
      {stages.map((s) => (
        <li
          key={s.name}
          className="flex items-center justify-between rounded-md border border-line bg-surface px-2.5 py-1.5 text-sm"
          style={
            s.state === "active"
              ? { borderColor: "var(--accent)" }
              : undefined
          }
        >
          <span className="font-medium">
            {s.name}
            {s.note ? <span className="ml-2 text-xs text-muted">{s.note}</span> : null}
          </span>
          <span className="font-mono text-xs tabular-nums text-muted">
            {s.ms !== undefined ? `${s.ms} ms` : "pending"}
          </span>
        </li>
      ))}
    </ol>
  );
}
