# Final System Review — §40 Audit (Swarm D, with §46 standard)

Date: 2026-09-10 · Auditor: Swarm D · Scope: `.` end-to-end (classify → retrieve → draft → escalate) · Evidence files cited per verdict.
Note: the master spec calls this "12 questions" but lists 13 bullets below (Problem…Differentiation). All 13 are audited; nothing skipped.

## Q1 — Problem: does it actually solve the exact problem? → PASS

Official problem = Hiver SDE Intern Twitter agent for AppleSupport (classify intents, grounded reply, escalate decision), preserved verbatim (`docs/research/problem/problem_decomposition.md §4`). Message-level 11-intent taxonomy, DM-redirect brand behavior, 2017 time-freeze, English-only scope — all documented assumptions, no simplification of the ask. `/predict` serves the full INPUT→intent+reply+decision→USER path live.

## Q2 — Data: are we using the supplied dataset correctly? → PASS

TWCS primary (`data/raw/twcs.csv`, 2.8M rows), Banking77 intent-only auxiliary. AppleSupport slice: 106,860 outbound → 89,694 deduped KB (template-cap 5) + 97,592 inbound pool. Preprocess NFKC/URL→\<URL\>/mention/emoji documented. No dataset replacement. Weak labels explicitly marked weak (GOLDEN_NOTE), headline = human-60.

## Q3 — AI: are models actually improving the result? → PARTIAL

TF-IDF+LogReg + rules beat trivial everywhere and beat keyword on escalation (esc_F1 0.471 vs 0.000) and groundedness (1.000 vs 0.205 ≥4-rate) — but LOSE on weak-trained intent (human-60 0.433 vs 0.517; weak-200 0.795 vs 1.000). Improvement is real on safety/escalation/groundedness, absent on intent (weak-label ceiling κ 0.465). No LLM in v1 (gated, correctly — unpinned LLM would add non-determinism without beating the ceiling). Verdict is PARTIAL, not FAIL: the model earns its place on the safety axis, disclosed in PER_INTENT.

## Q4 — Retrieval: is retrieval necessary and effective? → PARTIAL

Necessary: yes — templates are intent-generic; passage IDs are the only per-case grounding artifact. Effective: partially proven — TF-IDF-NN builds in 17s, p50 35ms, top-5 + IDs on every output; ablation shows -retrieval → groundedness 4.75→~3.0. But recall@k/MRR/NDCG unmeasured (owned by Swarm C), and F3 probe shows a link-only case auto-handling despite retrieval returning passages (score floor missing). Retrieval exists + serves + is cited; its quality number does not yet exist.

## Q5 — Agents: are agents actually necessary? → PASS

Correct answer implemented: NO agent framework. Fixed 5-step deterministic pipeline (validate→classify→retrieve→draft→escalate→validate) in plain Python + Pydantic dataclass. Rationale logged (compounding error 0.95¹⁰≈0.60, cost, non-determinism; `docs/research/agents/orchestration.md`). LangGraph-guardrail pattern emulated without the dependency. No agent-shaped code to justify.

## Q6 — Architecture: is every major component justified? → PASS

15 decisions in `docs/DECISION_LOG.md`, each with why + revisit trigger: no vector DB, no framework, templates>LLM, TF-IDF+LogReg, weak-bootstrap-as-draft, English-only, 4-trigger escalation, DM-as-triage, dual golden, heuristic judge, dedup-cap, stateless FastAPI. `docs/research/architecture/architecture_decision.md` carries the deterministic/ML/LLM/retrieval/agent split (§15). No marketing components found.

## Q7 — Evaluation: can we quantitatively demonstrate performance? → PARTIAL

Yes on human-60: intent 0.433/macro 0.443, esc P/R/F1 0.400/0.571/0.471, per-intent table + confusion CSV + top confusions (`evaluation/PER_INTENT.md`), heuristic groundedness 4.72/1.000, failure F1–F8 with real outputs. No on rigor bars: n=60 (±~12% CIs, per-intent support ≤13), single annotator (no inter-annotator κ), escalation recall 0.571 < 0.90 ship bar, LLM judge gated (κ≥0.60 + safety-recall≥0.90 unmet — correctly unshipped). Quantitative demonstration exists; ship-grade confidence does not — stated plainly in every report's limitations section.

## Q8 — Reliability: what happens when things fail? → PARTIAL

17 probes across F1–F8: 13 PASS, 3 PARTIAL (F5-evil-URL + F6-PII×2: safe drafts, missing escalate), 1 FAIL (F3 9-word link-only auto-handles). Empty/huge/injection/jailbreak/human-request all escalate safely; flame regression fixed + re-tested. Classifier exception → weak-label fallback (conf 0.35); retriever exception → empty passages → `no_grounding` escalate (fail-close). Missing: retry/backoff load evidence, rate-limit config, fresh-machine repro test (Swarm A owns). Fails are filed, not hidden — PARTIAL, trending to PASS after the 4 queued rule fixes.

## Q9 — Scalability: can the system handle the implied workload? → PARTIAL

Measured: p50 180ms / p95 192ms end-to-end (20-sample dev probe), retrieval p50 35ms, 44MB index, stateless FastAPI → workers→replicas→ANN path documented, $6–50/mo to 10k users. Unmeasured: cold start, p99, throughput, mem/CPU under load, Docker load test (Swarm C owns PERFORMANCE.md; frontend/ empty). Proportional per §9 (no K8s over-engineering) — but "measured on dev CPU" ≠ prod proof. PARTIAL.

## Q10 — Security: are obvious attack surfaces addressed? → PARTIAL

Addressed: no secrets in prompts/code, direct injection + jailbreak → escalate (F4/F8 5/5 PASS), drafts never echo PII (F6 output-safe), no action tools exist to hijack (no refund/email/send — blast radius nil by architecture), OWASP LLM01 treatment in `docs/SECURITY_REVIEW.md`. Gaps: PII-presence→escalate rule missing (F6 PARTIAL), no URL-allowlist (F5 PARTIAL), paraphrase/obfuscation untested, no formal scan output in repo. Fail-close posture real; depth incomplete. PARTIAL.

## Q11 — Cost: is the system economically reasonable? → PASS

$0 inference (CPU sklearn + joblib, no API calls), 44MB index, $6–12/12–25/25–50/mo at 100/1k/10k users vs $300–6k LLM-per-request. LLM path priced as labeled estimates ($0.0002–5/req), never as measured. No invented precision on costs; estimates marked ESTIMATE per §13. PASS.

## Q12 — Reproducibility: can another developer run it? → PARTIAL

README 7-command <15min path, `requirements.txt`, frozen seeds (42/7/11), all artifacts in-repo (`models/intent_classifier.pkl`, `data/processed/apple_kb.csv`, `data/indexes/`, `evaluation/*.csv`), `docs/REPRO_CHECK.md` started, `pytest tests -q` 4 pass. Missing: verified fresh-clone run log, frontend/ empty (Streamlit TODO), Docker compose untested. Reproducible in principle + largely in practice; not yet witnessed clean-room. PARTIAL.

## Q13 (§40 bullet 13) — Differentiation: why better than a generic LLM wrapper? → PASS

`docs/DIFFERENTIATION.md` argues with artifacts, not adjectives: thread-aware 89k KB + frozen templates with passage IDs (invention structurally impossible) + 4-trigger escalation with reason codes + dual golden with 39 published flips + disclosed circularity (we print our 1.000 and tell you not to cite it) + failure suite with open FAILs. Head-to-heads vs ldulcic seq2seq / Intercom Fin / X-RAG demo / keyword classifiers each state beat-conditions honestly, including where we lose (paraphrase, retrieval precision, resolution quality). §46 evidence bar — research, experiments, metrics, working code, failure handling, decision rationale — is met in-repo.

## Scoreboard

| # | question | verdict |
|---|---|---|
| 1 | Problem | PASS |
| 2 | Data | PASS |
| 3 | AI | PARTIAL |
| 4 | Retrieval | PARTIAL |
| 5 | Agents | PASS |
| 6 | Architecture | PASS |
| 7 | Evaluation | PARTIAL |
| 8 | Reliability | PARTIAL |
| 9 | Scalability | PARTIAL |
| 10 | Security | PARTIAL |
| 11 | Cost | PASS |
| 12 | Reproducibility | PARTIAL |
| 13 | Differentiation | PASS |

**5 PASS · 7 PARTIAL · 0 FAIL.** Zero FAILs because every known gap is measured, filed with a queued fix, and disclosed in-report — but seven PARTIALs mean: not shippable this week. The single highest-leverage close is full 200-human labeling (unblocks Q3/Q7) followed by the 4 escalation-rule fixes (unblocks Q8/Q10).

## §46 standard — survival answer

"Why believe this over a wrapper?" Because the repo contains: grounded IDs on every output, measured escalation with reason codes, dual golden with published flips and kappa ceilings, a failure suite with open FAILs, per-intent collapse tables, and a cost/latency profile a per-request LLM cannot touch — all reproducible offline in <15 minutes. The evidence is the argument.
