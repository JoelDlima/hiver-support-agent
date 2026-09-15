# Scaffold — hiver-deep-research-audit-058174

## User Prompt (VERBATIM — gospel)

See `query.md` in this run directory for the verbatim canonical research query.
Source: user-prompt (no `research/prompt.txt` present at bootstrap).
First line of original message: "You are running a HyperResearch deep-research run. Research query (verbatim, gospel — never paraphrase it):"
Followed by the full `# HIVER — DEEP RESEARCH + FORENSIC AUDIT + RE-ENGINEERING DIRECTIVE` block dated September 14, 2026, then the OpenCode-adapted router Procedure (steps 1-9 + tier/gears reminder), which is the WRAPPER (not part of the query).

## Run config

- vault_tag: hiver-deep-research-audit-058174
- query_file_path: research/runs/hiver-deep-research-audit-058174/query.md
- modality: synthesize (primary) + compare (secondary)
- profile/gear: full (55-80 sources, ~1.5-2.5h)
- expected tier: full (16 steps) — confirm after step 1 decomposition
- final report path: research/notes/final_report_hiver-deep-research-audit-058174.md (ship gate decides)
- project deliverable path (separate, per query): docs/FINAL_REPORT.md in Hiver workspace

## Modality classification rationale

- **synthesize** (primary): the query demands a defended position — which brand, intent taxonomy, architecture, retrieval, escalation policy, and evaluation design deserve trust — with evidence chains (benchmarks, leakage audits, human agreement). It asks "WHY" 15+ times, each backed by data/research/experiments.
- **compare** (secondary): at least several architectures (simple retrieval+LLM vs hybrid+rerank vs classifier+retrieval+calibrated escalation, etc.) and two baselines must be proportionately compared with a committed recommendation.
- NOT collect (not an enumeration), NOT forecast (no forward prediction horizon).

## Tier rationale (to fill after step 1)

- Placeholder: expecting `full` given multi-dimensional forensic audit (data, ML, retrieval, agents, backend, DB, eval, frontend, infra, scalability, security) + technology landscape + leakage/temporal/escalation/judge-agreement analyses. Confirm from prompt-decomposition.json.

## Wrapper requirements

- OpenCode adaptation of Claude Code router: bootstrap via hyperresearch CLI (init, install --steps-only, archive-run, vault-tag, run init --profile full), todo list per pipeline step, invoke step skills in tier order via skill tool, task-tool mapping (general = writers/investigators, explore = read-only surveys), vault CLI as source of truth, ship gate (retractions + run finish, max 3 fix rounds), no regeneration after step 11, no skipped steps, tool call in every message while subagents in flight.
- Scale gear `full`; tiers light/full/dissertation routing per router skill. Dissertation opt-in only (not requested).
- Research volume requested by query (~100-200 queries across landscape) maps to gear `full` (55-80 vault sources) — note tension: query asks more than gear provides; resolve by prioritizing high-impact dimensions (dataset/conversation reconstruction, leakage/temporal, intent taxonomy, retrieval, escalation calibration, LLM-judge agreement, baselines/eval) and recording the shortfall honestly in the report.
- Existing Hiver workspace (C:\Hiver) is audit target: inspect before rewriting; forensics across all layers; minimum-complexity principle.
