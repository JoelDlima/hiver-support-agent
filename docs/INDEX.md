# Documentation index

All written material for this project lives under `docs/`. The only other markdown
in the repository is the root [`README.md`](../README.md) and the evaluation
evidence under [`evaluation/`](../evaluation) (which is kept beside its CSV
artifacts so every number stays traceable).

## The deliverables (start here)

| Document | What it is |
|---|---|
| [`REPORT_VIRGIN_6PAGE.md`](REPORT_VIRGIN_6PAGE.md) | The 6-page report — problem framing, results vs two baselines, top-5 failure modes, "what is misleading about my headline number", next week. **This is the report referenced in the README.** |
| [`DECISION_LOG.md`](DECISION_LOG.md) | The 10–15 non-obvious decisions, each with the rejected alternative and a revisit trigger. |
| [`REPRO.md`](REPRO.md) | How to reproduce the headline results in under 15 minutes (fast path ≈1 min, full rebuild ≈6–8 min). |
| [`ANNOTATION_PROTOCOL.md`](ANNOTATION_PROTOCOL.md) | How the golden set was sampled, labelled, and adjudicated. |

## Research

| Directory | What it holds |
|---|---|
| [`research/`](research/INDEX.md) | The research trail: per-topic notes, paper digests, technology decisions, dataset quality scans, and the running research log. See its own [`INDEX.md`](research/INDEX.md). |
| [`research_log.md`](research_log.md) | Chronological research log (DATE / QUERY / SOURCE / FINDING / IMPACT). |

## Working documents

| Directory | What it holds |
|---|---|
| [`plans/`](plans) | Internal execution plans (win plan, fix plan, revamp plan, implementation plan, verification checks, submission checklist). |
| [`reviews/`](reviews) | Self-audits and positioning: red-team review, security review, differentiation, uniqueness, verdict. |
| [`archive/`](archive) | Superseded AppleSupport-era reports, kept for provenance only. Not current. |

## Evaluation evidence

Not markdown-only, so it stays outside `docs/`:

- [`evaluation/virgin/`](../evaluation/virgin) — golden set (`golden_human_200.csv`), headline results (`results_human200.csv`), baselines, judge agreement, failure tests, sampling note.
- [`evaluation/rubric.md`](../evaluation/rubric.md) — the LLM-as-judge rubric.

<p align="right">(<a href="../README.md">back to README</a>)</p>
