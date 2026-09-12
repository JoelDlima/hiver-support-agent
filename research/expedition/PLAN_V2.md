# PLAN_V2 — Detailed implementation (locked 2026-09-12, docs verified Sept 2026)

## Doc-verification record (all fetched 2026-09-12, before any code decision)
- Groq models: production = llama-3.1-8b-instant + llama-3.3-70b-versatile (BOTH
  Enterprise/ContactSales — DO NOT USE), openai/gpt-oss-120b ($0.15/$0.60),
  openai/gpt-oss-20b ($0.075/$0.30, ~1000 t/s), whisper. Preview (discontinuable):
  qwen3.6-27b, qwen3.8-27b, gpt-oss-safeguard-20b, llama-prompt-guard-2-22m/86m.
  Source: console.groq.com/docs/models.
- Strict mode (`strict:true`, constrained decoding) ONLY on gpt-oss-20b, gpt-oss-120b,
  qwen3.8-27b. Streaming + tool-use NOT supported with Structured Outputs.
  Source: console.groq.com/docs/structured-outputs.
- Free tier: 30 RPM / 1K RPD / 8K TPM / 200K TPD (gpt-oss + qwen). 429s carry
  retry-after + x-ratelimit-* headers. Source: console.groq.com/docs/rate-limits.
- Instructor 1.17.0 (MIT): current API is `instructor.from_provider("groq/<model>")`,
  install `pip install "instructor[groq]"`. Source: python.useinstructor.com/integrations/groq.
- Promptfoo: MIT (still OSS post-OpenAI), Node>=22.22 (local Node v24.19.0 OK),
  `npx promptfoo@latest` no-install, custom Python providers via file://, 60+ providers.
  Source: promptfoo.dev/docs (installation, getting-started, red-team/quickstart).
- PyPI (live, venv is py3.12): groq 1.7.0, instructor 1.17.0, rank-bm25 0.2.2,
  sentence-transformers 6.0.1, setfit 1.2.0, lightgbm 4.7.0, structlog 26.1.0,
  slowapi 0.1.10, tenacity 9.1.4, pybreaker 1.4.1, schemathesis 4.26.1, openai 3.13.0.

## Locked decisions (D1–D8)
- D1 Groq drafter → `openai/gpt-oss-20b` + strict:true + Instructor from_provider +
  Pydantic, existing £/HH:MM/URL gate UNCHANGED, fail-closed. qwen3.8 = preview,
  conditional arm only. llama-3.3-70b DROPPED (Enterprise pricing).
- D2 Prompt-guard: llama-prompt-guard-2-86m ($0.04/1M) CONDITIONAL injection screener,
  needs keyed test before adoption.
- D3 Free-tier pacing: keyed evals ≥2.5s apart; n≥100 studies split across days/RPD.
- D4 requirements.txt → freeze to venv-tested versions (sklearn 1.9.0-class), ADD
  groq/instructor pins; verify eval regenerates bit-identical CSVs.
- D5 Promptfoo via npx (no global install in repro); keyless default (custom python
  provider importing src.agent; llm-rubric asserts only when key present).
- D6 Heavy deps (torch/ST/setfit) DEFERRED to Phase 2 session (GB-scale downloads);
  this session: rank-bm25 + instructor + groq only (all <50MB).
- D7 No edits to golden CSVs, models/*.pkl, data/processed, frontend-next in Phase 0–1
  except additive files. Headline numbers must not move without a labeled retrain.
- D8 pytest stays green at every step; run_virgin_eval.py must reproduce
  results_human200.csv exactly after Phase 0–1 (no model changes).

## Phase 0 — Tier-0 fixes (THIS SESSION, Impl-A)
0.1 Sync UNIQUENESS.md (0.795/0.803, esc 0.767, money 0.850 17/20, 9/9 probes,
    Groq live via gpt-oss-20b pending re-pin).
0.2 REPORT_VIRGIN_6PAGE.md §2: esc 0.915/κ 0.715, money 0.850 (17/20).
0.3 ANNOTATION_PROTOCOL.md §3: money 0.850.
0.4 requirements.txt freeze + groq/instructor/rank-bm25 pins; README test-count 15→24.
0.5 agent.py: decide_escalation/draft_grounded defaults → brands_mod.DEFAULT_BRAND;
    comment that trivial/keyword baselines are Apple-scoped.
0.6 groq_draft.py: GROQ_MODEL → openai/gpt-oss-20b (+strict:true already), fallback
    qwen3.8-27b conditional; brands.py groq_model fields updated; Instructor path with
    graceful ImportError fallback to current JSON parsing (no hard dep at import).
0.7 Tests: re-pin assertions, new test for default-brand + strict schema shape.

## Phase 1 — Proof harness (THIS SESSION, Impl-B)
1.1 promptfooconfig.yaml (keyless): custom python provider (new file
    eval_providers/virgin_provider.py) calling AppleAgent(brand=virgin); asserts =
    contains/contains-any/regex/javascript (no llm-rubric by default); 30-case golden
    slice + 20-payload injection suite (static, from track-7 taxonomy).
1.2 scripts/confusion_virgin.py → evaluation/virgin/confusion_human200.csv (NEW file).
1.3 Bootstrap CIs (2000 resamples) + McNemar trivial/final + simple/final in
    run_virgin_eval.py; print CIs next to every delta; BASELINE_VS_FINAL.md gains §D
    (CI table). Must reproduce existing CSV values exactly.
1.4 Significance-gated CI wording: gate FLIPS not absolutes (promptfoo threshold).

## Phase 1b — Retrieval/KB additive (THIS SESSION, Impl-C)
1.5 NEW src/hybrid_retrieval.py: rank_bm25 stage-1 + RRF(k=60) fusion with existing
    TF-IDF-NN scores, flag-gated (env VIRGIN_HYBRID=0 default OFF); zero changes to
    current retriever when OFF.
1.6 Score-attached citations helper (rank/BM25/cosine/RRF/threshold flag) for UI.
1.7 NEW scripts/build_virgin_manifest.py: kb_manifest.json (content_sha256/row,
    corpus fingerprint, counts, params, git_sha) + 5-number quality card print.
    Read-only over existing CSVs; no changes to build_virgin_kb.py.
1.8 tests/test_hybrid_retrieval.py + manifest test. pytest green.

## Later phases (NOT this session)
P2: SetFit/MiniLM head, LightGBM arm, per-intent thresholds, coefficient explanations,
    AL loop, Parquet layer. P3: HITL review queue + autonomy matrix + correction loop.
P4: slowapi/tenacity/pybreaker, OTel JSONL, structlog, RFC-9457 envelope,
    React-Flow default graph, review-queue UI.

## File ownership (parallel agents — NO overlap)
- Impl-A: docs/UNIQUENESS.md, docs/REPORT_VIRGIN_6PAGE.md, docs/ANNOTATION_PROTOCOL.md,
  requirements.txt, README.md (2 numeric cells), src/agent.py, src/groq_draft.py,
  src/brands.py, tests/test_brand_groq.py (+1 new test file allowed).
- Impl-B: promptfooconfig.yaml (NEW), eval_providers/* (NEW), scripts/confusion_virgin.py
  (NEW), evaluation/virgin/confusion_human200.csv (NEW), scripts/run_virgin_eval.py,
  evaluation/virgin/BASELINE_VS_FINAL.md (§D append).
- Impl-C: src/hybrid_retrieval.py (NEW), scripts/build_virgin_manifest.py (NEW),
  evaluation/virgin/kb_manifest.json (NEW), tests/test_hybrid_retrieval.py (NEW).
- Shared read-only: everything else. Conflict rule: if your file isn't listed, don't touch it.
