# Hiver Breadth — Eval + Safety + Observability (2026-09-11)

Context: heuristic judge + gated LLM (pinned gpt-4o-mini hook behind wκ≥0.60 + safety-recall≥0.90), safety recall headline (1.000 on n=3 unclaimable / money 0.350 on n=20), red-team FAILs (virgin 5 PASS / 1 PARTIAL / 3 FAIL: F4a packed, F5 French-stranded, F6 money-gate; SELF D1–D8).
Method: 20 websearch queries (auto, 8 results each), all OK, no 429. Full DATE/QUERY ledger in `docs/research_log.md` (2026-09-11 breadth entry). No code/data/eval files touched.

## Table (20 topics)

| # | Topic | Key finding | Hiver relevance | Verdict |
|---|---|---|---|---|
| 1 | RAGAS faithfulness vs answer correctness | Faithfulness = supported/total claims, reference-free, 0.95 pairwise WikiEval (Es 2309.15217); correctness = factuality + semantic similarity vs gold, needs labels. Never average. | Heuristic judge is faithfulness-shaped, not span-grounded; dual-golden already gates both | KEEP dual-gate; queue span-attribution NLI week-2 |
| 2 | DeepEval G-Eval bias | G-Eval = CoT steps + form-filling + token-prob weighted sum; biases: position/verbosity/recency (+16% GPT-4o LitBench)/self-preference/format; judge bias varies per model → rankings distort; ≤2x data savings (ICLR-25) | Gated LLM must stay advisory until swap≥85% + reference-guided + CoT | ADOPT swap-both-orders + tie-on-flip |
| 3 | LangSmith vs Langfuse vs Braintrust | LangSmith = full lifecycle + 30+ eval templates + automation + managed deploy; Langfuse = MIT OSS self-host ClickHouse, deterministic online evals on roadmap; Braintrust = eval-first CI gates + bt CLI + Gateway $249 flat. All ingest OTEL. | Keep lightweight JSON logs (no lock-in); borrow trace→dataset + CI-gate pattern | DEFER vendor; ADOPT pattern |
| 4 | OpenTelemetry FastAPI tracing | `FastAPIInstrumentor.instrument_app(app, excluded_urls)` + hooks; 0.65b0 Jul-2026; auto via opentelemetry-instrument; exclude health/metrics | Backend already logs request_id JSON; OTEL adds retrieve→draft→escalate spans | ADOPT (TOP-3 #2) |
| 5 | Prometheus latency histograms | Histograms aggregatable via `histogram_quantile(0.95, sum(rate(bucket[5m])) by (le))`; `avg(quantile)` BAD; buckets around SLO (0.1/0.2/0.3/0.45) | /metrics avg-only hides tail; cold-start 808/1341ms vs claimed p50 180ms needs p50/p95 honesty | ADOPT (TOP-3 #2) |
| 6 | promptfoo scanner | MIT ~22k★, `redteam setup`, custom probes (injection/jailbreak/PII/contracts), YAML evals + CI action + code scanning | Freeze F4/F5/F8 as promptfoo YAML in CI, block on delta>0.05 | ADOPT (TOP-3 #1) |
| 7 | garak scanner | NVIDIA 8.1k★ Apache-2.0, probes promptinject/encoding/dan/atkgen-adaptive, `--target_type openai/rest` incl. Groq, OWASP tags v1, HTML report | Nightly encoding+promptinject vs Groq drafter; map hits to F4/F5 | ADOPT (TOP-3 #1) |
| 8 | Presidio PII | Analyzer (NER+regex+checksum+context + scores) → Anonymizer (replace/redact/mask/hash/encrypt); 9.7k★; overlap = higher-score wins; explicit no-guarantee | Replace regex-only with Presidio pre-egress + response-ingress scan, `[EMAIL_0001]` placeholders | ADOPT (TOP-3 #1) |
| 9 | OWASP LLM Top10 2025 | LLM01 injection, 02 disclosure, 03 supply-chain, 04 poisoning, 05 output-handling, 06 agency, 07 sys-prompt leak, 08 vector, 09 misinfo, 10 consumption; mitigations = segregate untrusted + least-privilege + schema-in-code + human approval | Hiver has no action tools (safety by absence); map F4→01, F5→01/08, F6→02/05, F8→09 | DOCUMENT mapping |
| 10 | Toxicity classifiers | Perspective (6 attrs 0-1, CNN+GloVe, German over-flag, code bypass, closure end-2026) insufficient alone; hybrid Perspective + Llama Guard 2 / Detoxify-local | Abuse path needs hybrid + per-category threshold + human gate, never fully-auto | ADOPT Detoxify-local first |
| 11 | Refusal / jailbreak benchmarks | JBB 200 + HarmBench 75 + AdvBench 51 + XSTest 250-safe/200-unsafe (over-refusal) + SorryBench 440 + MultiBreak 10.4k multi-turn (+54 ASR) | Expand F8 from 3/3 static to XSTest-safe + JBB slice + quarterly fresh payloads | ADOPT XSTest-safe metric |
| 12 | Kappa Landis-Koch | <0 poor, 0-0.20 slight, 0.21-0.40 fair, 0.41-0.60 moderate, 0.61-0.80 substantial, 0.81-1 almost-perfect; arbitrary + prevalence-sensitive → report raw+κ+CI+confusion | Bars (intent≥0.70 / esc≥0.60+raw≥0.85 / wκ≥0.60) = substantial threshold, defensible; virgin 0.772 vs Apple 0.465 flags assistance bias | KEEP bars |
| 13 | Power analysis n for kappa | Cantor/Flack + R kappaSize; κ~0.6 needs ~200 for CI width 0.10, N=50 width≥0.20; k0 0.6→k1 0.75 needs n≈177; n=20 CI 0.70-0.97 vs n=400 0.87-0.93 | Safety 1.000 (n=3) unclaimable; money 0.350 (n=20) better-powered; 60-overlap calibrates but underpowers | KEEP 200-golden minimum (TOP-3 #3) |
| 14 | Abstention / coverage | TACL survey: ACC, P_abs, Coverage=(N1+N2+N4)/N, Abstention Rate, Coverage@Acc, AURCC/AUACC, Abstain-ECE; risk-coverage tradeoff | F3 no-retrieval→abstain needs coverage + risk, not just pass rate | ADOPT Coverage@Acc + AURCC (TOP-3 #3) |
| 15 | Confusion-matrix per-intent | sklearn 1.9.0 `confusion_matrix` C[i,j]=true-i/pred-j, `labels=` fixed 11-order, normalize true/pred/all; macro unweighted vs weighted vs micro=accuracy | Already in PER_INTENT.md + confusion_human60.csv; keep raw + normalized-true | KEEP |
| 16 | Escalation calibration curves | `calibration_curve` + CalibrationDisplay reliability diagram (pred x vs true y) + ECE + isotonic/sigmoid; LogReg calibrated, NB over-confident | 0.6/0.8 thresholds uncalibrated; esc recall 0.459/0.500 vs ≥0.90 bar needs diagram first | ADOPT diagram + ECE before retune (TOP-3 #3) |
| 17 | Canary deploys for agents | MLflow-2026: 1%→5%→25%→50%→100%, session-sticky hash, shadow mirror zero-impact, judge+human rollback, hours soak; agent-canary OSS (MD5 router + p95 gates + auto-rollback) | Ship path for qwen→gpt-oss fallback chain; shadow new agent before promote | ADOPT shadow + staged promote (TOP-3 #2) |
| 18 | RAGAS limitations | WikiEval small-pairwise; RAGTruth 18k detector F1 only 52.7%, GPT-4 9.3% halluc; representation detectors fail to generalize; TRIVIA+ longest-ctx + noise stress | Corroborates never-average + faithful-but-wrong #1 failure; HHEM hi-prec vs RAGAS hi-rec tradeoff | KEEP pair-gate |
| 19 | Safety-recall / red-team FAIL taxonomy | ALERT 45k (6/32), AIRT XPIA top risk, llm-failure-taxonomy 6 classes (3e RAG-mismatch, 6c escalation-breakdown, 6d canary-gap); rail pattern = confident-ungrounded + client-only guardrails | Tag Virgin F1–F7 + D1–D8 to taxonomy (D1 money-gate HIGH, F4a/F5/F6 → 3a/3d/6c) | DOCUMENT tags |
| 20 | Heuristic + gated LLM | Heuristic = deterministic gate; LLM advisory until wκ≥0.60 + safety-recall≥0.90; judges inconsistent on OPMISUSE (low α, high overlap), SAGE-Eval <58%, R-Judge 74.45%; CSA = strict rubrics + sample-verify | Validates Hiver design; report raw + chance-corrected, never LLM-scores keyless | KEEP design |

## Top-3 upgrades (ordered by risk-reduction per effort)

### 1. Deterministic safety layer: Presidio + promptfoo + garak in CI (closes F5 PARTIAL, hardens F4a/F6)
Why: SELF D1 (money-gate near-dead on confident texts), F4a packed FAIL, F5 French-stranded FAIL, F5 URL-allowlist PARTIAL are all deterministic-filter problems, not model-capacity problems. Presidio + strict schema + scanners are the OWASP-load-bearing controls.
What:
- `presidio_analyzer` (en_core_web_sm first, lg if CPU allows) + `presidio_anonymizer` (replace `[EMAIL_0001]`-style, redact cards/keys) pre-egress AND response-ingress; log event never PII; custom recognizers for booking-ref / Delay-Repay refs.
- Freeze F4/F5/F8 as `promptfoo` YAML (direct + indirect + encoding + over-refusal XSTest-safe slice); `garak --probes promptinject,encoding,dan` nightly vs Groq drafter endpoint (REST target); block merge on ASR>0 or delta>0.05.
- Keep fail-closed: scanner unreachable/slow → block (already in eval_strategy §8).
Files: `src/text_norm.py` (+presidio path), `backend/main.py` (gateway hooks), new `evals/promptfoo/*.yaml`, CI job. No KB/golden changes.
Expected: F5 PARTIAL→PASS (allowlist + ingress scan), fewer confident-money leaks (D1 mitigated, not solved — `has_money` lexicon still needs H6 recalibration), reproducible ASR numbers for report.
Cost: S (Presidio sm ~100MB, CPU-only; promptfoo/garak offline, never in request path).

### 2. Honest observability: OTEL + Prometheus histograms + shadow/canary (fixes latency honesty, enables replay)
Why: Cold-start 808/1341ms vs claimed p50 180ms, avg-only /metrics, no trace hierarchy — cannot diagnose D3/D4/D5 or prove SLO. AI canary needs session-sticky + judge signals or Groq fallback ships blind.
What:
- `FastAPIInstrumentor.instrument_app(app, excluded_urls="healthcheck,metrics")` + server hook (request_id/intent/decision/latency_ms, never text/PII); keep existing JSON log line as event.
- Replace avg with `Histogram('http_request_duration_seconds', buckets=[0.05,0.1,0.2,0.3,0.45,0.65,1.0,2.0])`; alert `histogram_quantile(0.95, sum(rate(bucket[5m])) by (le)) > SLO`; report p50/p95 only (n=20 too small for p99).
- Shadow new agent (qwen→gpt-oss→template chain) mirroring prod traffic at zero impact + staged promote 1%→5%→25%→100% with success-rate + p95 + safety-recall gates; session-key hashing.
Files: `backend/main.py` (+3 OTEL lines + histogram), `frontend-next` /metrics poll unchanged, new `deployment/shadow.md` runbook. No model changes.
Expected: Honest p50/p95 panel, trace-to-dataset replay for every FAIL (Langfuse pattern without vendor), safe Groq pin migration (llama-3.3 sunset → qwen/gpt-oss).
Cost: S (2 deps, <20 lines; shadow is infra doc until traffic exists).

### 3. Eval rigor: calibration curves + coverage + powered kappa (fixes esc recall 0.459/0.500 vs ≥0.90 bar)
Why: Ship bar fails ~2x on escalation; 0.6/0.8 thresholds uncalibrated; 60-overlap CI too wide to license judge; faithful-but-wrong needs pair-gate discipline.
What:
- Plot `sklearn.calibration.calibration_curve` reliability diagram + ECE for escalation confidence on DEV; then per-intent threshold = cost(wrong)/cost(handoff); money/safety stay rule-based (never score-gated).
- Add Coverage, Coverage@Acc, AURCC + F3 abstention≥95% to every report; keep 11×11 raw + normalized-true confusion + per-intent P/R/F1 (labels=INTENTS, zero_division=0).
- Keep n=200 golden minimum (κ~0.6 → CI width 0.10); 60-overlap for calibration only; always bootstrap CI (2000 resamples); keep RAGAS faithfulness+correctness pair, never average (HHEM hi-prec vs RAGAS hi-rec).
Files: `scripts/` eval additions + `evaluation/*` report columns only. No serving-path changes.
Expected: Calibrated thresholds lift esc recall toward ≥0.90 without escalate-everything collapse; coverage exposes over-abstention; CI widths stop unclaimable safety-1.000 claims.
Cost: S (eval-only, CPU).

## Honest limits
- All 20 findings are websearch-sourced Sep-2026, not locally measured; versions/prices drift (Groq pins, Perspective closure end-2026, FAISS 1.15, FastAPI 0.141).
- No upgrade claims latency/accuracy lift without re-running `pytest` + golden + failure suite; safety recall stays n-limited until double-labeled 200 with κ.
- Only `.` touched (this file + research_log append).
