# Scaffold — hiver-support-agent-audit-6d951f

## User Prompt (VERBATIM — gospel)

See `query.md` for the verbatim canonical query. Summary of intent (not a substitute):
Forensic audit + re-engineering directive for the Hiver SDE Intern take-home: pick ONE brand from
Customer Support on Twitter (thoughtvector/customer-support-on-twitter, ~3M tweets), build intent
classifier + grounded reply generator + auto-handle/escalate decider, and prove trustworthiness via
golden set (150–250), evaluation harness, LLM-as-judge + human agreement, two baselines, 6-page
report, and 10–15 decision log. Existing workspace implementation is UNTRUSTED and must be
measured, challenged, and improved. Full directive text in the original user message is gospel.

## Run config

- vault_tag: hiver-support-agent-audit-6d951f
- query_file_path: research/runs/hiver-support-agent-audit-6d951f/query.md
- modality: synthesize (primary) + compare (secondary) + collect (tertiary)
- profile/gear: full (55–80 sources, triple draft, full critic suite)
- created: 2026-09-15T07:54:48+05:30

## Modality classification rationale

- **synthesize (primary):** The run must produce a defended thesis — which brand, intent taxonomy,
  retrieval strategy, escalation policy, evaluation design, and minimal architecture maximize
  trustworthiness per unit of complexity for THIS assignment. Evidence chains required.
- **compare (secondary):** At least several plausible architectures (simple retrieval+LLM vs hybrid
  +rerank+LLM vs classifier+retrieval+calibrated escalation, etc.) plus technology alternatives per
  capability must be proportionately compared with a committed recommendation.
- **collect (tertiary):** Broad technology landscape enumeration (data engineering, retrieval,
  storage, ML, LLMs, agent frameworks, eval, observability, deployment, security, testing) with
  named fields per option.

## Tier rationale

Classified: full tier + argumentative format. The query is a multi-paragraph forensic-audit and
re-engineering directive with contested decision points (brand selection, data-derived taxonomy,
leakage-safe splits, retrieval strategy, escalation calibration, judge-vs-human validity,
minimal-architecture thesis) requiring contradiction graph, loci analysis, depth investigation,
triple-draft ensemble, synthesis, critics, and patcher. No fiscal time_periods; time horizon is
2024–2026 technology verified as of September 14, 2026.

## Wrapper requirements

- Save path: `research/notes/final_report_<vault_tag>.md` (ship gate via `run finish`).
- Citation format: vault-note citations per pipeline shims; no invented URLs/numbers.
- Terminal sections: must cover brand choice, intent taxonomy, data splits, golden set, baselines,
  retrieval method, model choice, escalation policy, evaluation + judge + human agreement, failures,
  headline-number critique, trust argument, advantage over simple LLM wrapper — backed by data,
  research, experiments, or explicit engineering reasoning.
- Research artifacts expected by directive: research/{problem,data,brand,intents,retrieval,models,
  evaluation,llm-judge,escalation,technology,competitors,scalability,security,architecture}/,
  research_log.md, technology-decisions/, docs/FINAL_REPORT.md — these are downstream engineering
  artifacts, not the research report itself; the research report informs them.
