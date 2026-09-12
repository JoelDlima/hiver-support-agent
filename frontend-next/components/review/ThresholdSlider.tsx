"use client";

// Coverage-vs-risk grid copied from evaluation/virgin/thresholds.json
// (msp_floor.grid; source noted in caption). Static so the slider works
// without a backend round-trip; /review/matrix serves the same grid live.
const GRID: Array<{ t: number; coverage: number; acc: number; nAbstain: number }> = [
  { t: 0.3, coverage: 0.995, acc: 0.794, nAbstain: 1 },
  { t: 0.35, coverage: 0.99, acc: 0.793, nAbstain: 2 },
  { t: 0.4, coverage: 0.985, acc: 0.792, nAbstain: 3 },
  { t: 0.45, coverage: 0.97, acc: 0.799, nAbstain: 6 },
  { t: 0.5, coverage: 0.945, acc: 0.804, nAbstain: 11 },
  { t: 0.55, coverage: 0.9, acc: 0.8, nAbstain: 20 },
  { t: 0.6, coverage: 0.855, acc: 0.801, nAbstain: 29 },
  { t: 0.65, coverage: 0.81, acc: 0.802, nAbstain: 38 },
  { t: 0.7, coverage: 0.745, acc: 0.812, nAbstain: 51 },
];

export default function ThresholdSlider({
  value,
  onChange,
}: {
  value: number;
  onChange: (v: number) => void;
}) {
  const idx = GRID.reduce((best, g, i) => (Math.abs(g.t - value) < Math.abs(GRID[best].t - value) ? i : best), 3);
  const g = GRID[idx];
  return (
    <div className="rounded-[24px] border border-hairline bg-card p-6">
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal">Policy</p>
      <h3 className="mt-1 font-display text-xl font-semibold tracking-[-0.03em]">
        Abstention threshold → coverage vs risk
      </h3>
      <label htmlFor="thr" className="mt-3 block text-sm font-medium">
        Threshold <span className="font-mono tabular-nums">{g.t.toFixed(2)}</span>
      </label>
      <input
        id="thr"
        type="range"
        min={0}
        max={GRID.length - 1}
        step={1}
        value={idx}
        onChange={(e) => onChange(GRID[Number(e.target.value)].t)}
        className="mt-2 w-full"
        aria-valuetext={`threshold ${g.t.toFixed(2)}`}
      />
      <dl className="mt-3 grid grid-cols-3 gap-3 text-sm">
        <div>
          <dt className="text-xs text-muted">Coverage</dt>
          <dd className="font-mono font-semibold tabular-nums">{(g.coverage * 100).toFixed(1)}%</dd>
        </div>
        <div>
          <dt className="text-xs text-muted">Covered acc</dt>
          <dd className="font-mono font-semibold tabular-nums">{g.acc.toFixed(3)}</dd>
        </div>
        <div>
          <dt className="text-xs text-muted">Abstained (n=200)</dt>
          <dd className="font-mono font-semibold tabular-nums">{g.nAbstain}</dd>
        </div>
      </dl>
      <p className="mt-3 text-xs text-muted">
        Production gate 0.45 (src/agent.py low_conf): coverage 97.0%, abstains 6/200 to the
        review queue. Raising the bar cuts auto-coverage for +0.01 acc — the risk dial.
        Source: evaluation/virgin/thresholds.json.
      </p>
    </div>
  );
}
