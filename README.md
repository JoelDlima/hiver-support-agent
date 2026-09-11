# Hiver — Support Agent (VirginTrains primary, AppleSupport kept) — all inside `C:\Hiver`

AI support agent, now **VirginTrains primary** (UK rail: Delay Repay + amendment + timetable) with **AppleSupport kept** as v1 evidence + transfer proof. Classifies intent (Virgin 10 / Apple 11 classes), drafts grounded reply from per-brand historical resolutions, decides auto-handle vs escalate with reason. Proof > system: golden sets + harness + baselines + failure analysis.

## Headline results — VirginTrains (primary)

Brand **VirginTrains**: 27,817 outbound / 37,444 inbound pool (union 65,346; Oct–Nov 2017 burst 91%), **10 intents** (`delay_claim, ticket_change_refund, timetable_platform, lost_property, complaint_service, fare_ticketing, accessibility_assistance, howto_guidance, support_access_followup, other_out_of_scope`). Golden **200** (`evaluation/virgin/golden_human_200.csv`: 60 manual-style + 140 rulebook-assisted, 41 flips, weak-vs-human acc 0.795 κ 0.772).

| set | system | intent acc / macroF1 | esc P/R/F1 | ground ≥4 |
|---|---|---|---|---|
| weak-200 (circular — do not cite) | trivial / simple / final | 0.095/0.017 – 1.000/1.000 – 0.795/0.793 | 0.000 – 0.303 – 0.641 | 0.000 – 0.015 – 0.935 |
| **human-200 (headline)** | trivial / simple / final | 0.075/0.014 – 0.795/0.801 – **0.660/0.672** | 0.000 – 0.238 – **0.667** (P 0.580 R 0.784) | 0.000 – 0.015 – **0.935** (mean 4.21) |

Baselines: **trivial** (majority + canned, never-escalate) vs **simple** (virgin keyword + top-1 copy) vs **final** (TF-IDF LogReg + virgin NN k=5 + template + rail rules). Final trades intent (−0.135 acc vs simple — weak-label ceiling) for escalation (+0.429 esc_F1) + groundedness. Safety recall **1.000 on n=3 human legal_safety (tiny — gate NOT claimable)**; money recall 0.800 (16/20); esc-vs-human acc 0.855 κ 0.577. Judge = heuristic offline + LLM hook, **gated (wκ ≥0.60 + safety-recall ≥0.90 to ship, else advisory; LLM unrun, no key)** — see `evaluation/virgin/JUDGE_AGREEMENT.md`. Failures F1–F7 exact-text re-probe 2026-09-11: 7 PASS / 2 PARTIAL / 0 FAIL (F4a packed now escalates via safety addon but intent still other→PARTIAL; F5 French + F6 repeat-refund fixed by language/money gates; F7 receipt still misrouted→PARTIAL; F2 exact passes, bare "still running?" variant still misses→fragility note) — see `evaluation/virgin/FAILURE_TESTS.md`. Index 27,172 docs, build 0.5s, p50 7.1ms; Apple end-to-end p50 180ms/p95 192ms. Repro **2.3 min** Apple pipeline (CPU) + Virgin KB/index scripts below. Full report: `docs/REPORT_VIRGIN_6PAGE.md` §1–6 (framing/not-built, baselines + Apple transfer row, top-5 failures, misleading, next-week incl. Groq, decisions pointer). Re-verified 2026-09-11: `run_virgin_eval.py` + `run_virgin_judge.py` re-ran clean (weak-vs-human acc 0.795 κ 0.772); README numbers now match `results_human200.csv`/`BASELINE_VS_FINAL.md` exactly.

## Virgin quickstart (revamp V2, CPU-only, Windows PowerShell)

```powershell
# 0. venv (already at C:\Hiver\.venv; if fresh:)
py -3.12 -m venv C:\Hiver\.venv
C:\Hiver\.venv\Scripts\Activate.ps1
pip install -r C:\Hiver\requirements.txt

# 1. pipeline (Apple v1 still works; Virgin KB/index already built)
$env:PYTHONPATH="C:\Hiver"
python C:\Hiver\scripts\build_virgin_kb.py        # -> data/processed/virgin_kb.csv (27,172), virgin_inbound_pool.csv (37,444)
python C:\Hiver\scripts\build_virgin_index.py     # -> data/indexes/virgin/ (TF-IDF NN, p50 ~7ms)
python -m pytest C:\Hiver\tests -q                # all pass (apple regression + virgin/groq fail-closed)

# 2. API (brand optional, default virgin; apple still served)
uvicorn backend.main:app --host 127.0.0.1 --port 8000  # from C:\Hiver
curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"text":"my train from Euston was delayed 45 mins, how do I claim Delay Repay?","brand":"virgin"}'
curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"text":"my iphone battery drains fast after ios 11 update","brand":"apple"}'
curl http://127.0.0.1:8000/metrics  # per-brand + totals

# 3. demo — Next.js + three.js (modern, live technicals)
cd C:\Hiver\frontend-next; npm install; $env:FASTAPI_URL="http://127.0.0.1:8000"; npm run dev  # :3000
# Shows, all measured live: pipeline stage ms, confidence bars, 3D retrieval graph + ranked scores,
# SSE-streamed Groq draft tokens, escalation+reason, heuristic judge, /metrics poll. See frontend-next/README.md.
# Legacy Streamlit (no server): streamlit run C:\Hiver\frontend\app.py
```

## Groq key instructions (optional live drafter; keyless default)

No key needed for any gate — template path is default and Groq fails closed to template.

```powershell
# 1. set key in env only (never in code; never log it)
$env:GROQ_API_KEY="gsk_..."  # or OPENAI_API_KEY as fallback; unset = template path (reason no-key)

# 2. client (already wired in src/groq_draft.py; for manual use):
# from groq import Groq  # pip install groq (in .venv)
# client = Groq()  # reads GROQ_API_KEY env
# model = "qwen/qwen3.8-27b"  # preview, 450tps, 131k ctx; fallback "openai/gpt-oss-120b" (prod, $0.15/0.60, 500tps)
# non-stream: temperature=0.6, max_completion_tokens=2048, top_p=0.95, response_format=json_schema strict
# stream: same minus response_format (stream+response_format=400), parse tokens, reasoning_effort="default" with retry-without fallback

# 3. fail-closed note: no-key / no-client / error / validation-fail (too-long, ungrounded £/HH:MM/URL) -> template.
#    UI/API show draft_path (template|groq) + groq_reason (no-key|no-client|validation-fail:*|error|ok).
#    Free tier ~30 RPM (qwen 429s observed live -> gpt-oss fallback proven) — never on critical path, never bulk in eval gates.
```

## Apple v1 quickstart (kept)

```powershell
# 1. venv (already at C:\Hiver\.venv; if fresh:)
py -3.12 -m venv C:\Hiver\.venv
C:\Hiver\.venv\Scripts\Activate.ps1
pip install -r C:\Hiver\requirements.txt  # + kagglehub pandas scikit-learn for data prep

# 2. data (all inside C:\Hiver\data\raw\)
# primary: twcs.csv 2,811,774 rows (kagglehub thoughtvector/customer-support-on-twitter, CC BY-NC-SA 4.0)
# secondary: banking77_train.csv (10,003) + banking77_test.csv (3,080), 77 intents (PolyAI GitHub, CC-BY-4.0, intent design only)

# 3. pipeline (verified 2.3 min total, CPU)
$env:PYTHONPATH="C:\Hiver"
python C:\Hiver\scripts\build_kb.py            # -> data/processed/apple_kb.csv (89k), apple_inbound_pool.csv (97k)
python C:\Hiver\scripts\build_retrieval_baseline.py  # -> data/indexes/ (TF-IDF NN, p50 ~35ms)
python C:\Hiver\scripts\train_classifier.py   # -> models/intent_classifier.pkl (30k weak labels)
python C:\Hiver\scripts\build_golden.py        # -> evaluation/golden_v1.csv (200 stratified weak-draft)
python C:\Hiver\scripts\human_correct_60.py    # -> evaluation/golden_human_60.csv (60 manual, flips=39)
python C:\Hiver\scripts\human_review_200.py    # -> evaluation/golden_human_200.csv (200: 60 manual + 140 assisted)
python C:\Hiver\scripts\run_eval.py            # weak-200 -> evaluation/results.csv
python C:\Hiver\scripts\eval_human60.py        # human-60 -> evaluation/results_human60.csv
python C:\Hiver\scripts\run_judge_agreement.py # judge: safety 0.909, esc F1 0.582 -> JUDGE_AGREEMENT_V2.md
python -m pytest C:\Hiver\tests -q             # 10 pass
python C:\Hiver\scripts\smoke_fail.py
```

API (brand-aware; `brand` optional, default `virgin`):
```powershell
$env:PYTHONPATH="C:\Hiver"
uvicorn backend.main:app --host 127.0.0.1 --port 8000  # from C:\Hiver
curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"text":"my iphone battery drains fast after ios 11 update"}'
curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"text":"my iphone battery drains fast after ios 11 update","brand":"apple"}'
```

## Headline results — Apple (transfer reference, kept)

**Weak-200 (circular — golden labels ARE keyword outputs, see misleading section):**

| system | intent_acc | macroF1 | esc_F1 | ground≥4 |
|---|---|---|---|---|
| trivial | 0.095 | 0.016 | 0.000 | 0.000 |
| simple keyword+BM25 | **1.000** | **1.000** | 0.727 | 0.205 |
| final TFIDF-LogReg+NN+template+rules | 0.795 | 0.796 | 0.600 | **1.000** |

**Human-60 (trustworthy — 60 blind-reviewed, 39 flips, weak-vs-human intent κ=0.465):**

| system | intent_acc | macroF1 | esc_P | esc_R | esc_F1 |
|---|---|---|---|---|---|
| trivial | 0.217 | 0.032 | 0.000 | 0.000 | 0.000 |
| simple | **0.517** | **0.547** | 0.000 | 0.000 | 0.000 |
| final | 0.433 | 0.443 | **0.368** | **0.500** | **0.424** |

Final loses intent to simple on human-60 because both train on weak labels (ceiling = weak-human 0.517); wins escalation (simple never escalates safety) + groundedness + latency p50 180ms/p95 192ms. See `docs/FINAL_REPORT.md` §16-18 + `evaluation/` for per-intent, confusion, failure suite.

## Layout (all inside C:\Hiver)

```
C:\Hiver\
  src/ (text_norm, intents, virgin_intents, brands, groq_draft, classifier, retriever, agent brand-aware)
  backend/main.py (FastAPI /predict brand-aware, /healthz, /readyz, /metrics per-brand)
  frontend/app.py (Streamlit brand switcher Virgin default, Apple alt)
  scripts/ (build_kb, build_retrieval_baseline, train_classifier, build_golden, human_correct_60, run_eval, eval_human60, smoke_fail, build_virgin_kb, build_virgin_index)
  models/intent_classifier.pkl  data/processed/apple_kb.csv + virgin_kb.csv  data/indexes/apple(legacy) + virgin/
  evaluation/ (golden_v1.csv, golden_human_60.csv, results.csv, results_human60.csv, rubric.md, virgin/SAMPLING_NOTE.md)
  research/ (10 tracks + architecture/ + technology-landscape.md)
  docs/FINAL_REPORT.md + REPORT_VIRGIN_6PAGE.md  tests/  deployment/Dockerfile.simple
```

Brands: **VirginTrains primary** (27,817 outbound, Delay Repay + amendment + timetable; see `research/datasets/virgin_data_quality.md`) + **AppleSupport kept** (106,860 replies, v1 evidence + transfer proof; iOS11/iPhoneX era, DM-triage voice; see `research/problem/problem_decomposition.md`).

## What is misleading about headline number?

Simple's 1.000 on weak-200 is **circular** (eval labels = its own rules). True ceiling is weak-vs-human 0.517. Final's 0.795 likewise optimistic. Trust human-60 + escalation + groundedness, not weak-200 accuracy. Full disclosure in report § “misleading”.

## Decisions (15 + Virgin addendum)

See `docs/DECISION_LOG.md` (15 Apple v1 non-obvious + 5-line Virgin addendum: why Virgin, brand-agnostic, Groq-behind-gate, rail safety add-ons, money-intent escalation). Virgin report: `docs/REPORT_VIRGIN_6PAGE.md`.

## Cite / borrow

TF-IDF/LogReg, BM25-style NN, FastAPI, AppleSupport data (CC BY-NC-SA 4.0, Kaggle thoughtvector). Banking77 inspected for intent design, not used for training (insufficient Twitter overlap). All research sources logged in `research/research_log.md`.
