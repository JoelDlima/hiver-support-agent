# Graph Report - Hiver  (2026-09-13)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1017 nodes · 1771 edges · 90 communities (60 shown, 23 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 25 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `211dbcdb`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22
- Community 23
- Community 24
- Community 25
- Community 26
- Community 27
- Community 28
- Community 29
- Community 30
- Community 31
- Community 32
- Community 33
- Community 34
- Community 35
- Community 36
- Community 37
- Community 38
- Community 39
- Community 40
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45
- Community 46
- Community 47
- Community 48
- Community 49
- Community 50
- Community 51
- Community 52
- Community 53
- Community 54
- Community 55
- Community 56
- Community 57
- Community 58
- Community 59
- Community 60
- Community 61
- Community 62
- Community 63
- Community 64
- Community 65
- Community 66
- Community 67
- Community 68
- Community 69
- Community 70
- Community 73
- Community 75
- Community 76
- Community 80
- Community 81
- Community 82
- Community 84
- Community 85
- Community 86
- Community 88
- Community 92
- Community 93

## God Nodes (most connected - your core abstractions)
1. `AppleAgent` - 40 edges
2. `normalize()` - 22 edges
3. `cn()` - 22 edges
4. `FASTAPI_URL` - 20 edges
5. `react` - 20 edges
6. `VirginRetriever` - 18 edges
7. `Retriever` - 17 edges
8. `draft_with_groq()` - 16 edges
9. `compilerOptions` - 16 edges
10. `PLAN_V2 — Detailed implementation (locked 2026-09-12, docs verified Sept 2026)` - 16 edges

## Surprising Connections (you probably didn't know these)
- `HybridVirginRetriever` --uses--> `VirginRetriever`  [INFERRED]
  src/hybrid_retrieval.py → scripts/run_virgin_eval.py
- `get_agent_for_brand()` --uses--> `AppleAgent`  [INFERRED]
  frontend/app.py → src/agent.py
- `test_agent_empty()` --calls--> `AppleAgent`  [EXTRACTED]
  tests/test_agent.py → src/agent.py
- `test_agent_escalate_human()` --calls--> `AppleAgent`  [EXTRACTED]
  tests/test_agent.py → src/agent.py
- `test_groq_no_key_returns_none()` --calls--> `draft_with_groq()`  [EXTRACTED]
  tests/test_brand_groq.py → src/groq_draft.py

## Import Cycles
- None detected.

## Communities (90 total, 23 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (66): _brand_summary(), _build_inspect_record(), _build_llm_block(), _collect_passages(), _do_review_transition(), embed2d(), eval_run(), EvalRunIn (+58 more)

### Community 1 - "Community 1"
Cohesion: 0.10
Nodes (45): Connection, _load_existing_hashes(), main(), Path, Promote reviewer corrections to golden candidates (Phase 3). Reads…, _sha(), _append_audit(), build_warm_transfer() (+37 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (46): LogisticRegression, NEEDS_ARTIFACT, _bootstrap_ci(), _embed_cached(), main(), Train the VirginTrains SetFit/MiniLM CHALLENGER head (Phase 2A, report-only).…, balanced_weak_sample(), build_head() (+38 more)

### Community 3 - "Community 3"
Cohesion: 0.14
Nodes (17): attach_citation(), HybridVirginRetriever, is_hybrid_enabled(), Hybrid BM25 + TF-IDF-NN retrieval over the VirginTrains KB (Phase 1b, item…, True iff VIRGIN_HYBRID env var is a truthy value. Default OFF., BM25 tokenizer: lowercase + whitespace split. Mirrors the lowercasing applied…, Reciprocal Rank Fusion score: sum(1 / (k + rank)) over 1-indexed ranks., Score-attached citation helper (item 1.6) for UI display. Fields per passage:… (+9 more)

### Community 4 - "Community 4"
Cohesion: 0.11
Nodes (26): apply_thresholds(), main(), _operating_point(), ndarray, Phase 2B post-hoc decision policy for the frozen VirginTrains intent model.…, Chosen threshold + metrics at that point + curve summaries., Gate one argmax prediction through the post-hoc policy. proba: {intent:…, _background_mean() (+18 more)

### Community 5 - "Community 5"
Cohesion: 0.12
Nodes (16): dependencies, class-variance-authority, clsx, dagre, framer-motion, geist, lucide-react, next (+8 more)

### Community 6 - "Community 6"
Cohesion: 0.12
Nodes (17): _key_status(), main(), Groq smoke: runs with/without key, prints draft_path per case. - No key…, main(), Mine safety/money slice from virgin pool for powered recall reporting.…, AppleAgent, Brand-agnostic agent (name kept for backward compat). Default brand=virgin., _fake_groq_module() (+9 more)

### Community 7 - "Community 7"
Cohesion: 0.12
Nodes (22): breaker_latency_probe(), call_groq_with_resilience(), call_with_retry(), _exclude_429(), get_http_client(), _is_429(), _is_retryable(), Phase 4A: shared httpx client + tenacity retry (429/5xx-only) + pybreaker. -… (+14 more)

### Community 8 - "Community 8"
Cohesion: 0.17
Nodes (15): eval_system(), main(), Ablation: isolate retrieval + classifier contributions on golden_human_60.…, evaluate(), groundedness_heuristic(), main(), DataFrame, Evaluation harness: intent, escalation, retrieval, reply-judge (heuristic,… (+7 more)

### Community 9 - "Community 9"
Cohesion: 0.16
Nodes (19): bootstrap_delta_cis(), evaluate(), groundedness_heuristic(), main(), adapt_final(), make_simple_fn(), fn(), mcnemar_exact() (+11 more)

### Community 10 - "Community 10"
Cohesion: 0.10
Nodes (20): Decision Log — 15 non-obvious decisions (Hiver AppleSupport), Addendum — balanced retrain + PII/DR30 + judge v2 (2026-09-11, keyed), Addendum — keyed LLM-judge study (2026-09-11, Groq key via env only), Addendum — post-freeze keyword fixes (2026-09-11, private working repo), Addendum — Virgin revamp V2 (Phase 2 V-APP, 2026-09-10), cache_resource, get_agent_for_brand(), _intents_for_brand() (+12 more)

### Community 11 - "Community 11"
Cohesion: 0.14
Nodes (13): BADGE_PILL, buildJudgeCurl(), buildPredictCurl(), buildStreamCurl(), CurlButton(), Judge, RunLogEntry, shellQuote() (+5 more)

### Community 12 - "Community 12"
Cohesion: 0.11
Nodes (17): EvalDoneSchema, EvalErrorSchema, EvalItemSchema, InspectLlmSchema, InspectRecordPayload, JudgePayload, JudgeSchema, PassagePayload (+9 more)

### Community 13 - "Community 13"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 14 - "Community 14"
Cohesion: 0.20
Nodes (18): _api_key(), _client(), _draft_json_schema(), draft_with_groq(), _empty_usage(), _extract_usage(), _prompts(), Groq live drafter (openai/gpt-oss-20b primary + qwen/qwen3.8-27b conditional… (+10 more)

### Community 15 - "Community 15"
Cohesion: 0.27
Nodes (10): Virgin judge agreement (judge-v1-2026-09-10, brand=virgin), What is misleading (mandatory), heuristic_judge(), JudgeScore, llm_judge(), LLM-as-judge rubric + harness. Offline heuristic default; optional OpenAI-…, main(), Judge-human agreement: heuristic judge vs human labels on golden_human_200… (+2 more)

### Community 16 - "Community 16"
Cohesion: 0.11
Nodes (17): name, private, scripts, build, dev, start, version, autoprefixer (+9 more)

### Community 17 - "Community 17"
Cohesion: 0.22
Nodes (11): main(), Train intent classifier on weak labels from inbound pool., build_pipeline(), load(), predict(), _preproc(), Pipeline, TF-IDF + LogReg intent classifier with weak-label bootstrapping. CPU-only. (+3 more)

### Community 18 - "Community 18"
Cohesion: 0.18
Nodes (13): ReviewPage(), act(), onKey(), Stats, ReviewItem, ReviewRow(), CLS, SlaChip() (+5 more)

### Community 19 - "Community 19"
Cohesion: 0.18
Nodes (11): Graph Report - graphify-out  (2026-09-13), Communities (80 total, 23 thin omitted), Community Hubs (Navigation), Corpus Check, God Nodes (most connected - your core abstractions), Graph Freshness, Import Cycles, Knowledge Gaps (+3 more)

### Community 20 - "Community 20"
Cohesion: 0.29
Nodes (6): build_pipeline(), main(), Pipeline, Train VirginTrains intent classifier on weak labels from virgin inbound pool.…, VirginTrains intent taxonomy (Phase 1 V-DATA filled, V-MODEL shim origin). 10…, # NOTE: agent._intent_assets reads THIS list (not brands.py). "crammed" covers…

### Community 21 - "Community 21"
Cohesion: 0.17
Nodes (10): RetrievalGraph3D, EmbedScene(), isFiniteNum(), passageColor(), Scene(), usePositions(), EmbedPoint, Passage (+2 more)

### Community 22 - "Community 22"
Cohesion: 0.23
Nodes (14): buildEmbedCurl(), buildPassagesCurl(), formatMs(), isEscalateDecision(), Page(), appendRunLog(), loadEmbed(), loadJudge() (+6 more)

### Community 23 - "Community 23"
Cohesion: 0.33
Nodes (3): Inspector(), InspectRecordSchema, InspectRecord

### Community 24 - "Community 24"
Cohesion: 0.19
Nodes (12): buildSteps(), formatStepMs(), layoutGraph(), nodeTypes, PipelineFlow(), PipelineFlowProps, PipelineStepState, StepDef (+4 more)

### Community 26 - "Community 26"
Cohesion: 0.21
Nodes (9): Badge(), BadgeProps, badgeVariants, Button, ButtonProps, buttonVariants, class-variance-authority, clsx (+1 more)

### Community 27 - "Community 27"
Cohesion: 0.27
Nodes (9): heuristic_escalate(), main(), Build golden eval set: 200 stratified + documented sampling. Human-reviewable…, main(), Expand to 200 human-reviewed (60 manual + 140 rulebook-assisted + spot-check).…, v2_esc(), v2_intent(), features_for_escalation() (+1 more)

### Community 28 - "Community 28"
Cohesion: 0.24
Nodes (8): main(), Build Apple KB: outbound AppleSupport replies deduped + inbound Apple threads…, main(), Build VirginTrains KB: outbound VirginTrains replies deduped + inbound mention…, normalize(), test_agent_empty(), test_agent_escalate_human(), test_normalize()

### Community 29 - "Community 29"
Cohesion: 0.06
Nodes (38): Virgin failure tests — real pool probes on final (brand=virgin), F1 — delay claim without booking ref (must not invent thresholds/times; must ask, F2 — timetable question with a specific time (must NEVER invent/confirm times), F3 — lost property: item detail (F3a) + callback PII (F3b), F4 — overcrowding language: colloquial vs lexicon (the lexicon-shape gap), F5 — non-English stranded passenger (must escalate, never English-auto-handle), F6 — money recall gap: repeat refund chase auto-handled, F7 — lost-ticket-with-receipt misrouted to lost property (intent miss cascades p (+30 more)

### Community 30 - "Community 30"
Cohesion: 0.15
Nodes (18): CurlCopy(), Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle, Tabs() (+10 more)

### Community 31 - "Community 31"
Cohesion: 0.24
Nodes (8): find_roots(), load_virgin_subset(), main(), DataFrame, Reconstruct VirginTrains conversation threads from the raw TWCS dump (Phase…, Chunked read of raw; keeps only Virgin-related rows., Walk each tweet's in_response_to chain to its structural root. Returns…, Series

### Community 32 - "Community 32"
Cohesion: 0.14
Nodes (15): configure_structlog(), emit_pipeline_spans(), force_flush(), get_logger(), get_tracer(), init_tracing(), JSONLSpanExporter, Phase 4A: OTel SDK (no collector) JSONL file exporter + structlog JSON wiring.… (+7 more)

### Community 33 - "Community 33"
Cohesion: 0.29
Nodes (9): Claim, claimPassageOverlap(), EvidenceView(), EvidenceViewProps, formatScore(), Link, splitClaims(), STOP (+1 more)

### Community 34 - "Community 34"
Cohesion: 0.36
Nodes (9): content_hash(), git_sha(), has_url(), is_boilerplate(), is_non_english(), main(), near_hash(), near_normalize() (+1 more)

### Community 35 - "Community 35"
Cohesion: 0.18
Nodes (11): display, metadata, mono, sans, NAV_LINKS, SiteHeader(), ThemeToggle(), framer-motion (+3 more)

### Community 36 - "Community 36"
Cohesion: 0.21
Nodes (14): force_breaker_open(), get_breaker_state(), reset_breaker(), fixture, Phase 4A: backend hardening + observability + safety. Covers: slowapi 429 shape…, _reset_breaker(), _reset_limiter(), tclient() (+6 more)

### Community 37 - "Community 37"
Cohesion: 0.33
Nodes (8): adjudicate(), heuristic_escalate(), main(), Build VirginTrains golden-200: weak-draft stratified + human-reviewed (60…, Weak-draft escalate label (human must review/override)., Single-annotator adjudication core (used for both manual-60 and assisted-140).…, stage1_weak(), stage2_human()

### Community 38 - "Community 38"
Cohesion: 0.36
Nodes (8): content_fingerprint(), convert(), load_created_at_map(), main(), DataFrame, Path, Build processed parquet data layer for VirginTrains (Phase 2C). Reads (READ-…, tweet_id -> created_at (UTC) from raw TWCS dump, read with usecols only.

### Community 39 - "Community 39"
Cohesion: 0.22
Nodes (8): call_api(), _get_agent(), Promptfoo custom Python provider (keyless): AppleAgent(VirginRetriever(),…, Lazy singleton: VirginRetriever + AppleAgent(brand="virgin")., Promptfoo entry point. Returns {"output": json} (never raises)., Minimal reader over data/indexes/virgin (built by…, VirginRetriever, test_off_mode_parity_with_virgin_retriever()

### Community 41 - "Community 41"
Cohesion: 0.32
Nodes (6): EvalRunner(), run(), Row, Summary, timestamp(), parseEvalPayload()

### Community 42 - "Community 42"
Cohesion: 0.29
Nodes (3): find(), AppleSupport subset inspection for TWCS dataset., union()

### Community 43 - "Community 43"
Cohesion: 0.39
Nodes (7): Path, Phase 2C data-layer tests: parquet round-trip, manifest fingerprint, thread…, _require(), test_al_csv_has_300_rows_with_strategy_mix(), test_manifest_fingerprint_still_verifies(), test_parquet_round_trip_row_counts(), test_thread_orphans_logged()

### Community 44 - "Community 44"
Cohesion: 0.20
Nodes (3): EvalDone, EvalItem, PredictResponse

### Community 45 - "Community 45"
Cohesion: 0.25
Nodes (8): build_context(), harden_system_prompt(), Phase 4A: retrieved-content sandboxing. KB passages are untrusted data (tweets…, Wrap one passage in <UNTRUSTED-TWEET> tags (truncated, never raises)., Build a sandboxed context block for up to k passages. Returns a string already…, Append the never-obey sandbox rule to a system prompt (idempotent)., wrap_passage(), test_sandbox_tags_in_prompt()

### Community 46 - "Community 46"
Cohesion: 0.18
Nodes (9): PLAN_V2 — Detailed implementation (locked 2026-09-12, docs verified Sept 2026), Doc-verification record (all fetched 2026-09-12, before any code decision), File ownership (parallel agents — NO overlap), Later phases (NOT this session), Locked decisions (D1–D8), Phase 0 — Tier-0 fixes (THIS SESSION, Impl-A), Phase 1 — Proof harness (THIS SESSION, Impl-B), Phase 1b — Retrieval/KB additive (THIS SESSION, Impl-C) (+1 more)

### Community 47 - "Community 47"
Cohesion: 0.47
Nodes (5): embed(), embedding_backend(), main(), Active-learning candidate selection over the Virgin inbound pool (Phase 2C).…, MiniLM only if already installed; else TF-IDF. Never installs anything.

### Community 48 - "Community 48"
Cohesion: 0.50
Nodes (3): RunAgainDiff(), Tok, wordDiff()

### Community 49 - "Community 49"
Cohesion: 0.60
Nodes (4): clean(), ddg(), main(), 120 meaningful DuckDuckGo searches (12x10 tracks) for Hiver. All inside…

### Community 50 - "Community 50"
Cohesion: 0.60
Nodes (4): clean(), ddg(), main(), Resume DDG from #50 onwards (1-based). Incremental save, slow, UA rotation.…

### Community 52 - "Community 52"
Cohesion: 0.67
Nodes (3): clean(), main(), Baseline retrieval repro: TF-IDF + sklearn NearestNeighbors over AppleSupport…

### Community 53 - "Community 53"
Cohesion: 0.67
Nodes (3): clean(), main(), Build VirginTrains TF-IDF + NearestNeighbors index (Phase 1 V-MODEL). Reads:…

### Community 54 - "Community 54"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/three, typescript

### Community 68 - "Community 68"
Cohesion: 0.38
Nodes (6): bootstrap_delta_ci(), main(), DataFrame, Phase 2B LightGBM baseline arm (REPORT-ONLY, timeboxed). Compares a LightGBM…, Percentile 95% CIs for (LGBM-LogReg) deltas on acc/macroF1. Deterministic., weak_sample()

### Community 80 - "Community 80"
Cohesion: 0.29
Nodes (7): Virgin baseline vs final — formal tables (brand=virgin), A. Weak-200 (keyword labels — CIRCULAR, do not use as headline), B. Human-200 (HEADLINE: single-annotator AI-assisted review), C. Per-intent F1 on human-200 (simple vs final; support in brackets), D. Uncertainty: bootstrap 95% CIs + McNemar (Phase 1, Impl-B), Interpretation (post balanced-retrain honesty), What is misleading (mandatory)

### Community 81 - "Community 81"
Cohesion: 0.29
Nodes (7): EXPEDITION LEDGER — Deep Technical Research (2026-09-11/12), ADOPT list (worth implementing under take-home constraints), Codebase audit vs ideal (assume-poor-then-verify method), Ideal architecture (synthesized from tracks), REJECT list (complexity without proof value), Search count by track (112 total, deduplicated by topic reservation), Unresolved (need humans/keys, not more searches)

### Community 82 - "Community 82"
Cohesion: 0.14
Nodes (12): Annotation + LLM-Judge Run Protocol (keyed n=30 study done 2026-09-11), 1. Second annotator (inter-annotator κ — PACK READY, needs a human), 2. LLM-judge run (first keyed run DONE 2026-09-11 — see `evaluation/virgin/LLM_J, 3. Mined-slice supporting evidence (done keyless, 2026-09-11), LLM-as-Judge Agreement Study — Virgin spotcheck_30 (n=30, 2026-09-11), Follow-up v2 + Groq A/B (keyed, same day — Temp script `ab_v2.py`, outputs commi, Groq-vs-template judged comparison (same judge, same rubric, n=30), Next (needs key + time) (+4 more)

### Community 84 - "Community 84"
Cohesion: 0.40
Nodes (4): do_drafts(), do_judge(), _llm_score(), Groq LLM-as-judge agreement study on virgin spotcheck_30 (n=30). Key via…

### Community 86 - "Community 86"
Cohesion: 0.40
Nodes (5): Virgin Golden-200 — Sampling Note (Phase 1 V-DATA), Context + adjudication rules, Pool + weak-label strata (first-match, followup-last; circular — stratify only), Rare money/safety oversampling (deliberate), Repro

### Community 88 - "Community 88"
Cohesion: 0.50
Nodes (4): LEDGER WAVE-2 — Domains A–M (2026-09-12, ~158 searches; expedition total ~270/300), Per-domain deltas (ADOPT/CONDITIONAL deltas vs wave-1; REJECTs extend wave-1 lis, Revised-tier inputs (for chat delivery), SearXNG infrastructure verdict (honest)

### Community 92 - "Community 92"
Cohesion: 0.23
Nodes (11): Hiver autonomy matrix v1 — intent x risk-tier x confidence-band -> route., gen(), decide_escalation(), draft_grounded(), _intent_assets(), _predict_for_brand(), Brand-agnostic agent: classify -> retrieve -> draft (groq then template) ->…, Try per-brand joblib model(s); fallback to weak_label (conf 0.35). (+3 more)

## Knowledge Gaps
- **197 isolated node(s):** `Judge`, `RunLogEntry`, `WidgetStatus`, `Stage`, `InspectRecordPayload` (+192 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 453 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `0. venv` connect `Community 29` to `Community 0`, `Community 16`, `Community 20`, `Community 14`?**
  _High betweenness centrality (0.352) - this node is a cross-community bridge._
- **Why does `react` connect `Community 18` to `Community 33`, `Community 35`, `Community 41`, `Community 11`, `Community 48`, `Community 16`, `Community 51`, `Community 21`, `Community 23`, `Community 24`, `Community 26`, `Community 30`?**
  _High betweenness centrality (0.142) - this node is a cross-community bridge._
- **Why does `AppleAgent` connect `Community 6` to `Community 0`, `Community 39`, `Community 8`, `Community 9`, `Community 10`, `Community 28`, `Community 15`, `Community 83`, `Community 84`, `Community 92`, `Community 29`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `AppleAgent` (e.g. with `get_agent_for_brand()` and `test_default_brand_and_strict_schema_shape()`) actually correct?**
  _`AppleAgent` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `normalize()` (e.g. with `main()` and `main()`) actually correct?**
  _`normalize()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Judge`, `RunLogEntry`, `WidgetStatus` to the rest of the system?**
  _197 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.060718252499074414 - nodes in this community are weakly interconnected._