# Detailed Implementation Plan — every clause of HIVER-MASTER-RESEA (2602 lines, read forward + backwards to line 2602)

Source verified: `C:\Users\Joel\Downloads\HIVER-MASTER-RESEA (1).txt`, 2602 lines, last line “A technology can be excellent while still being wrong for this particular project.” Backwards read 2602→2588 verified. Official problem = Hiver SDE Intern Twitter agent (AppleSupport). All work inside `C:\Hiver`.

## Clause → owner → artifact → status

| Clause | Requirement | Owner | Artifact | Status |
|---|---|---|---|---|
| §1 source of truth | preserve exact problem, no simplification, doc assumptions | done | research/problem/problem_decomposition.md §4 | DONE |
| §2 objective | robust/scalable/measurable/repro end-to-end, not LLM wrapper | done | src/agent.py deterministic | DONE |
| §3 workspace | Hiver root + structure | done | C:\Hiver tree | DONE |
| §4 phase 0 | research before code | done | 10 agents first | DONE |
| §5 deep research 100–200 | meaningful searches, parallel agents | swarm-consol | research/research_log.md (14 lines now → 100+) | PARTIAL → swarm |
| §6 time window Sep 10 2026 + 1–2y | ecosystem 2025–26 | done/swarm | per-track docs | DONE (verify dates) |
| §7 freshness | version/API/license/pricing per tech | swarm-B | tech-decisions 001–006 | PARTIAL |
| §8 10 tracks | agents 1–10 outputs | done | 10 md files | DONE |
| §9 scalability proportional | stateless, no K8s over-eng | done | production.md + main.py | DONE |
| §10 dataset not replaced | TWCS primary, Banking77 intent-only | done | data/raw/twcs.csv + GOLDEN_NOTE | DONE |
| §11 baseline | naive baseline measured | done | trivial + keyword in run_eval | DONE |
| §12 evidence architecture | architecture_decision per component | done | research/architecture/architecture_decision.md | DONE |
| §13 decision matrix | table Quality/Speed/Cost/... no invented numbers | swarm-B | research/technology-decisions/MATRIX.md | TODO |
| §14 no marketing | every tech earns place | done | DECISION_LOG | DONE |
| §15 LLM usage split | deterministic/ML/LLM/retrieval/agent split | done | architecture_decision | DONE |
| §16 no wrapper | prove leverage vs prompt→LLM | done | hybrid + eval | DONE |
| §17 retrieval eng | chunk/index/metadata/hybrid/rerank/cite + measure separately | swarm-C | retrieval metrics file | PARTIAL (TFIDF only, add recall@k) |
| §18 model routing | small→cheap, complex→strong, only if benefit | done | template + (LLM gated) | DONE (documented) |
| §19 structured output | JSON Schema/Pydantic/validation | done | AgentResult dataclass + /predict schema | DONE (add JSON schema file) |
| §20 reliability | validation/conf/retry/fallback/empty/API-fail | swarm-A | reliability tests | PARTIAL (add retry/fallback test) |
| §21 eval first-class | evaluation/ + normal/difficult/edge/noisy/adversarial | swarm-D | harness + golden | PARTIAL (expand suite) |
| §22 metrics | choose relevant only | done | acc/macroF1/esc PRF/ground/latency | DONE |
| §23 baseline vs final | table Metric/Baseline/Final/Impr | swarm-C | evaluation/BASELINE_VS_FINAL.md | PARTIAL (have CSV, need formal) |
| §24 ablation | remove components one-by-one | swarm-C | evaluation/ABLATION.md + run | TODO |
| §25 differentiation | why better than GPT/RAG/agent | swarm-D | docs/DIFFERENTIATION.md | TODO |
| §26 real end-to-end | INPUT→...→USER, no mocks/TODOs | done | /predict live | DONE |
| §27 failure testing | empty/huge/corrupt/outage/timeout/malformed/no-retrieval/etc | swarm-D | evaluation/FAILURE_TESTS.md + run | PARTIAL (smoke only) |
| §28 performance | cold/warm/p50/p95/p99/throughput/mem/CPU/GPU/tokens/DB/retrieval | swarm-C | evaluation/PERFORMANCE.md + run | PARTIAL (p50/p95 only) |
| §29 cost | per-req/user/100/1k/10k + ingest/embed/retrieval | swarm-C | evaluation/COST.md | PARTIAL (estimates only) |
| §30 security | secrets/keys/input/injection/leakage/auth/SSRF | swarm-A | SECURITY_REVIEW.md + scan | PARTIAL |
| §31 observability | logs/IDs/tracing/latency/error/usage/cost metrics | swarm-A | backend logging + METRICS | PARTIAL |
| §32 reproducibility | README install/config/load/index/run/eval | swarm-A | README + repro test | PARTIAL (test fresh) |
| §33 document research | research/README | done | research/README.md | DONE |
| §34 research log | DATE/QUERY/SOURCE/FINDING/RELEVANCE/IMPACT | swarm-consol | research_log 100+ | PARTIAL (14 lines) |
| §35 tech decision log | 001-vector-db, 002-llm, ... | swarm-B | 6 files | TODO |
| §36 no pretend | verified vs inference vs hypothesis | done | academic_review labels | DONE (enforce everywhere) |
| §37 iterative | implement→measure→fix→retest | done | flame/injection fix | DONE |
| §38 not prototype | MVP→prod core, correctness first | done | backend + tests | DONE |
| §39 UI/UX secondary | clear in/out/status/errors/evidence/confidence | swarm-A | frontend/ Streamlit | TODO (empty) |
| §40 final review | 12 questions audit | swarm-D | docs/FINAL_REVIEW.md | TODO |
| §41 deliverables | research/impl/docs/validation lists | consol | this plan + FINAL_REPORT | PARTIAL |
| §42 final report 24 secs | 1 exec ... 24 how-to-run | swarm-D | docs/FINAL_REPORT_V2_24SEC.md | PARTIAL (condensed v1) |
| §43 most important | sound/defensible, DATA+ALGO+...+EVAL | done | all | DONE |
| §44 start now 20 steps | parse→...→report | done/in-progress | this plan | IN PROGRESS |
| §45 no permission | proceed autonomously | done | swarm launch | DONE |
| §46 final standard | why better than wrapper? evidence | swarm-D | FINAL_REVIEW | TODO |
| D1–D17 discovery | full landscape, no anchor, combos, non-AI, OSS+closed, prod experiences, pipeline, landscape-by-capability, min-components, measurable-problem, emergent arch, audit | swarm-B | TECHNOLOGY_AUDIT.md | PARTIAL |

## DuckDuckGo research protocol (mandatory for swarm)
Use `webfetch https://duckduckgo.com/html/?q=<query>` + `websearch` for cross-check. Log every query to `research/research_log.md` as DATE/QUERY/SOURCE/KEY FINDING/RELEVANCE/IMPACT. Minimum 5 DDG queries per swarm agent (≈25 new, total →100+).

## Swarm launch (4 groups, all inside C:\Hiver, venv C:\Hiver\.venv, PYTHONPATH=C:\Hiver)
- Swarm A: frontend + observability + security + reproducibility + reliability extras
- Swarm B: MATRIX + 001–006 + TECHNOLOGY_AUDIT + landscape expansion + freshness verify
- Swarm C: BASELINE_VS_FINAL + ABLATION + PERFORMANCE + COST + retrieval recall@k
- Swarm D: per-intent/confusion + LLM-judge attempt + FAILURE_TESTS + DIFFERENTIATION + FINAL_REVIEW + FINAL_REPORT_V2_24SEC
- Consol (main): merge research_log to 100+, verify every artifact, run pytest + eval + API smoke
