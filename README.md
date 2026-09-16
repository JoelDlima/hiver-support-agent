<a id="readme-top"></a>

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)](requirements.txt)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=nextdotjs&logoColor=white)](frontend-next/package.json)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688?style=for-the-badge&logo=fastapi&logoColor=white)](backend/main.py)
[![Data CC BY-NC-SA 4.0](https://img.shields.io/badge/Data-CC_BY--NC--SA_4.0-lightgrey?style=for-the-badge)](https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter)

<br />
<div align="center">

<h3 align="center">Hiver — VirginTrains Support Agent</h3>

  <p align="center">
    VirginTrains primary agent: classifies intent (10 classes, TF-IDF + LogReg — 0.795 acc / 0.803 macroF1 on human-200, Δ +0.005 vs keywords = noise, CI [−0.015,+0.025] p=1.0), drafts grounded RAG replies, triages auto-handle vs escalate-with-reason (esc F1 0.767, Δ +0.529 — the real win).
    <br />
    <a href="docs/REPORT_VIRGIN_6PAGE.md"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="#usage">View Demo</a>
    &middot;
    <a href="#contact">Report Bug</a>
    &middot;
    <a href="#contact">Request Feature</a>
  </p>
</div>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

## About The Project

VirginTrains is the primary brand (UK rail: Delay Repay + amendment + timetable). AppleSupport is kept as v1 evidence + transfer proof. The agent classifies intent, retrieves grounded passages from per-brand historical resolutions, drafts a template reply (≤280 chars, no invented £/HH:MM/URL), and decides `auto_handle` vs `escalate` with a reason. Proof over system: golden sets + harness + baselines + failure analysis. All paths inside `C:\Hiver`.

10 Virgin intents (`src/virgin_intents.py`):

`delay_claim, ticket_change_refund, timetable_platform, lost_property, complaint_service, fare_ticketing, accessibility_assistance, howto_guidance, support_access_followup, other_out_of_scope`

Brand pool (source: `docs/REPORT_VIRGIN_6PAGE.md` §1): 27,817 outbound / 37,444 inbound pool (union ≈65.3k pre-dedup rows; exact union varies by dedup — see SAMPLING_NOTE strata sum 37,444). Index: 27,172 docs, 19,898 feats, build ~0.5–0.6s, p50 ~7–8ms / p95 ~8–9ms dev-CPU (ranges: `data/indexes/virgin/index_meta.json` reports 0.6s/7.9/8.7ms, `RETRIEVAL_ABLATION.md` virgin_nn k=5 ctx0 reports 7.1/8.2ms — same order of magnitude, machine-dependent).

Headline — human-200 (source: `evaluation/virgin/results_human200.csv`, `evaluation/virgin/BASELINE_VS_FINAL.md` §B). Golden `evaluation/virgin/golden_human_200.csv`: 60 manual-style + 140 rulebook-assisted, 41/200 intent flips, weak-vs-human acc 0.795 κ 0.772, single-annotator (no inter-annotator κ yet).

| system | intent acc / macroF1 | esc P / R / F1 | ground mean / ≥4 rate |
|---|---|---|---|
| trivial (generic canned, never-escalate) | 0.075 / 0.014 | 0.000 / 0.000 / 0.000 | 3.00 / 0.000 |
| simple (virgin keyword + top-1) | 0.790 / 0.796 | 1.000 / 0.135 / 0.238 | 2.33 / 0.015 |
| final (TF-IDF LogReg + virgin NN k=5 + template + rules) | **0.795 / 0.803** | **0.778 / 0.757 / 0.767** | **4.21 / 0.900** |

Deltas final−simple on human-200: acc +0.005, macroF1 +0.007, esc_F1 +0.529 (source: `BASELINE_VS_FINAL.md` §B). Balanced `class_weight` retrain fixed the accessibility tail (0.500 → 0.848, matching simple); final ≥ simple on 9/10 per-intent F1, trails only `delay_claim` (source: `BASELINE_VS_FINAL.md` §C).

Circular reference — weak-200 (source: `BASELINE_VS_FINAL.md` §A, do not cite as headline): trivial 0.095/0.017 esc 0.000 ground 3.00/0.000; simple 0.975/0.974 esc 1.000/0.179/0.303 ground 2.33/0.015; final 0.970/0.970 esc 0.694/0.893/0.781 ground 4.21/0.900. Deltas final−simple: acc −0.005, macroF1 −0.004, esc_F1 +0.478. Weak labels were frozen with pre-fix keyword rules, so post-fix simple scores 0.975 (the 5 misses ARE the fixed cases); train-subset acc 0.969 is equally circular. Golden sampling: stratified from 37,444 inbound pool, 10 strata × ~20, seed 7, rare oversample (accessibility 20/148 near-census, lost/howto 20 each ~6%), context = current + ≤2 prior turns, 133 cross-brand agent rows excluded (source: `evaluation/virgin/SAMPLING_NOTE.md`).

Baselines: **trivial** = majority + canned, never-escalate; **simple** = virgin keyword rules (post-fix) + virgin NN top-1 copy; **final** = TF-IDF LogReg (`models/intent_virgin.pkl`, 30k weak post-fix, `class_weight=balanced`) + virgin NN k=5 + virgin templates (delay with DR30 bands) + brand-aware triggers (rail SAFETY_ADDONS, money intents, crowd remap, PII gate) (source: `BASELINE_VS_FINAL.md` header).

Judge gate (source: `evaluation/virgin/JUDGE_AGREEMENT.md`): heuristic offline + LLM hook, ship gate `wκ ≥ 0.60 + safety-recall ≥ 0.90`, currently **advisory-only**. Esc-vs-human: acc 0.915 κ 0.715 (P 0.778 R 0.757 F1 0.767). Safety recall 1.000 on n=3 human `legal_safety` (tiny — CI ~0.4–1.0, gate NOT claimable); money recall 0.850 on n=20 human `money_threshold`. Groundedness judge-harness heuristic: mean 4.32, ≥4 rate 1.000 (template-shaped, circular by design); eval-harness heuristic on the same 200: mean 4.21, ≥4 rate 0.900 (source: `results_human200.csv`). Keyed LLM-judge studies (run on Groq `qwen/qwen3.8-27b`, temp 0, n=30, source: `evaluation/virgin/LLM_JUDGE_30.md`; live drafter now `openai/gpt-oss-20b` + conditional `qwen/qwen3.8-27b` preview fallback): v1 (no passages) verdict κ 0.253, groundedness wκ 0.060 → gate holds, advisory-only; v2 (passage texts + double-run, self-consistency 1.000) verdict κ −0.005 → gate holds twice. Groq draft A/B on same 30: 29/30 live drafts, 1 too-long rejected by gate, specificity upgrade only — template stays default.

Failure probes (source: `evaluation/virgin/FAILURE_TESTS.md`): exact-text re-probe 2026-09-11 post-fix F1–F7, 9 probes: **9 PASS / 0 PARTIAL / 0 FAIL** (was 5/1/3 on 2026-09-10). Regression tests: `tests/test_virgin_fixes.py`. F1 draft states DR30 bands; F3b fires `pii_review` on the phone regex itself (number NOT echoed).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* Python 3.12 (source: `requirements.txt` header) — `numpy==2.5.3`, `pandas==3.0.5`, `scikit-learn==1.9.0` (TF-IDF + LogReg intent, NN retrieval), `scipy==1.18.1`, `joblib==1.6.0`
* FastAPI `0.141.1` + `uvicorn==0.52.4` — `backend/main.py` (`/predict` brand-aware, `/healthz`, `/readyz`, `/metrics` per-brand)
* Next.js 14 (`next ^14.2.18` in `frontend-next/package.json`) + React 18.3.1 + three.js / `@react-three/fiber` + `framer-motion` + `tailwindcss` — demo UI on `:3000`
* Streamlit `1.63.0` — legacy demo `frontend/app.py` (no server)
* pytest `9.1.1` + `httpx==0.28.1` — `tests/` (75 passed) incl. `test_virgin_fixes.py`, `test_brand_groq.py`, `test_win_plan_a.py`
* Groq optional drafter behind gate (`src/groq_draft.py`, key via env only, fail-closed to template)

### V2 (2026-09-15)

V2 closes the Win-Plan workstreams and FIX_PLAN hygiene items — every change verified end-to-end (75 pytest + `npm run build` + live backend/frontend smoke of all 13 endpoints and the full HITL loop):

- **Proof endpoints**: `POST /judge/groundedness` (claim-level entailment; Groq `gpt-oss-20b` temp-0 primary, deterministic offline heuristic fallback), `POST /eval/retrieval-ablation` (8 arms), `GET /eval/compare` (file-cached brand matrix), `offline` flag on `/predict` + `/predict/stream`.
- **3-tab demo** (`Try it / Proof / Review`) with zod-validated live payloads; 3D graph + log tail demoted to Advanced disclosures (R5 two-tier demo).
- **Honest baseline (R1a)**: pre-fix keyword rules reconstructed from git history and rescored on human-200 — final-vs-teacher delta **+0.020 acc (CI [−0.035, +0.080])**, **+0.572 esc F1** (`evaluation/virgin/R1_PREFIX_BASELINE.md`).
- **Miss audit (R1b)**: all 41 human-200 misses bucketed — 41% OOS/noise, 27% ambiguous, 29% model-error (`evaluation/virgin/MISS_AUDIT.md`).
- **Portability**: zero hardcoded `C:\Hiver` paths in code (all resolved from `__file__`); `requirements.txt` synced with the venv; Dockerfile rewritten for `backend.main:app`; blinded IAA pack + `compute_iaa.py` ready for the annotator hour (R4).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

CPU-only, Windows PowerShell. Backend on `:8000`, frontend on `:3000`. No key needed for any gate — template path is default.

### Prerequisites

* Python 3.12 (`py -3.12`)
* Node.js ≥18.17 + npm (for `frontend-next` — Next.js 14)
* Git (to inspect `evaluation/`, `docs/`)
* Optional only for live drafts: `GROQ_API_KEY` in env (never in code/logs)
* Optional only for full data rebuild: `pip install kagglehub` then `kagglehub dataset download thoughtvector/customer-support-on-twitter` → place `twcs.csv` at `data/raw/twcs.csv` (gitignored; frozen-path repro does not need it)

Notes: `/predict` + `/predict/stream` + `/review/enqueue` + `/eval/*` + `/embed2d` + `/judge/groundedness` are rate-limited to 5/min/IP (429 + `Retry-After: 60`) — pace live demo clicks. `HIVER_OFFLINE=1` forces template-only drafts (no LLM calls, `offline: true` echoed). Frontend needs `FASTAPI_URL` per shell or a `frontend-next/.env.local` copy of `.env.example`. Beyond loopback, set `HIVER_API_KEY` on BOTH backend and frontend envs — review mutations + stream/eval routes then require it (BFF forwards server-side; open demo when unset). Review/inspect payloads retain raw customer text (needed for human triage) — treat the queue DB as PII runtime state (gitignored, shorten retention, never publish).

```powershell
py -3.12 --version
node --version; npm --version
Test-Path C:\Hiver\requirements.txt
Test-Path C:\Hiver\frontend-next\package.json
```

### Installation

```powershell
# 0. venv
py -3.12 -m venv C:\Hiver\.venv
C:\Hiver\.venv\Scripts\Activate.ps1
pip install -r C:\Hiver\requirements.txt

# 1. build Virgin KB + index (already built; re-runnable CPU)
$env:PYTHONPATH="C:\Hiver"
python C:\Hiver\scripts\build_virgin_kb.py      # -> data/processed/virgin_kb.csv (27,172), virgin_inbound_pool.csv (37,444)
python C:\Hiver\scripts\build_virgin_index.py   # -> data/indexes/virgin/ (TF-IDF NN)

# 2. train (balanced retrain; 30k weak post-fix)
python C:\Hiver\scripts\train_virgin.py         # -> models/intent_virgin.pkl

# 3. verify
python -m pytest C:\Hiver\tests -q
```

Repo layout (all inside `C:\Hiver`):

```text
C:\Hiver\
  src/ (text_norm, intents, virgin_intents, brands, groq_draft, classifier, retriever, agent brand-aware)
  backend/main.py (FastAPI /predict brand-aware, /healthz, /readyz, /metrics per-brand)
  frontend-next/ (Next.js 14 demo, :3000)
  frontend/app.py (legacy Streamlit demo)
  scripts/ (build_virgin_kb, build_virgin_index, train_virgin, run_virgin_eval, run_virgin_judge, run_llm_judge_30, build_annotation_pack, apple v1 scripts)
  models/intent_virgin.pkl
  data/processed/virgin_kb.csv + virgin_inbound_pool.csv
  data/indexes/virgin/
  evaluation/virgin/ (golden_human_200.csv, results_human200.csv, BASELINE_VS_FINAL.md, JUDGE_AGREEMENT.md, LLM_JUDGE_30.md, SAMPLING_NOTE.md, FAILURE_TESTS.md, annotation_pack_50.csv)
  docs/REPORT_VIRGIN_6PAGE.md + DECISION_LOG.md + ANNOTATION_PROTOCOL.md
  tests/test_virgin_fixes.py
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

> **Reproduce the headline in <15 min** (PS requirement): committed artifacts make it a 2-command run — `python scripts/run_virgin_eval.py` + `python -m pytest tests -q`. Full path in [`docs/REPRO.md`](docs/REPRO.md).

```powershell
$env:PYTHONPATH="C:\Hiver"
# backend
uvicorn backend.main:app --host 127.0.0.1 --port 8000  # from C:\Hiver

# predict (brand optional, default virgin)
curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"text":"my train from Euston was delayed 45 mins, how do I claim Delay Repay?","brand":"virgin"}'
curl http://127.0.0.1:8000/metrics  # per-brand + totals

# eval (headline numbers re-verified 2026-09-11 post-fix; must match results_human200.csv + BASELINE_VS_FINAL.md)
python C:\Hiver\scripts\run_virgin_eval.py    # -> evaluation/virgin/results_human200.csv + results_weak200.csv
python C:\Hiver\scripts\run_virgin_judge.py   # -> evaluation/virgin/JUDGE_AGREEMENT.md inputs
python -m pytest C:\Hiver\tests -q            # incl. 9/9 failure-probe regressions

# demo UI (new terminal)
cd C:\Hiver\frontend-next; npm install; $env:FASTAPI_URL="http://127.0.0.1:8000"; npm run dev  # :3000
# Shows, all measured live: pipeline stage ms, confidence bars, 3D retrieval graph + ranked scores,
# SSE-streamed Groq draft tokens, escalation + reason, heuristic judge, /metrics poll.
# Legacy Streamlit (no server): streamlit run C:\Hiver\frontend\app.py
```

Groq key (optional live drafter; keyless default; fail-closed to template):

```powershell
# set key in env only (never in code; never log it)
$env:GROQ_API_KEY="gsk_..."  # unset = template path (reason no-key)
# fail-closed: no-key / no-client / error / validation-fail (too-long, ungrounded £/HH:MM/URL) -> template.
# UI/API show draft_path (template|groq) + groq_reason (no-key|no-client|validation-fail:*|error|ok).
# Live drafter: openai/gpt-oss-20b temp 0 (fallback qwen/qwen3.8-27b conditional preview; prior n=30 study ran on qwen/qwen3.8-27b, source: evaluation/virgin/LLM_JUDGE_30.md). Free tier ~30 RPM — never on critical path, never bulk in eval gates.
```

_For more examples, please refer to the [Virgin 6-page report](docs/REPORT_VIRGIN_6PAGE.md) and [BASELINE_VS_FINAL](evaluation/virgin/BASELINE_VS_FINAL.md)._

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Roadmap

Done (source: `docs/DECISION_LOG.md` lines 28–30; `evaluation/virgin/FAILURE_TESTS.md`):

- [x] `class_weight=balanced` retrain — accessibility tail 0.500 → 0.848, headline 0.795/0.803 (no hand-rolled oversampling)
- [x] PII gate (already done — NOT queued): `has_pii` phone/email regex → `pii_review` before `human_request`; F3b fires on the number itself, templates have no PII slots so echo is structurally impossible
- [x] DR30 bands in delay template (already done): hedged "typically" 30–59 ≈ 50% single / 60+ ≈ 100% / 120+ ≈ return + booking-ref ask, ≤280 chars
- [x] Judge v2 + Groq A/B reported against the gate (both kept advisory): passages + double-run self-consistency 1.000 but κ −0.005; A/B 29/30 live drafts, specificity only, template stays default
- [x] Failure probes 9/9 green + `tests/test_virgin_fixes.py` regressions (timetable `still running`, crowd remap, amend reprint/receipt cues)
- [x] `frontend-next` demo (:3000) + per-brand `/metrics` + brand-agnostic dict (`DEFAULT_BRAND=virgin`)
- [x] **V2**: groundedness/ablation/compare endpoints + V3 study (wκ 0.007 gate FAIL reported honestly), retrieval ablation table, 3-tab demo, offline flag, honest pre-fix baseline + miss audit, portability (no hardcoded roots), Dockerfile rewrite, blinded IAA pack ready

Queued (source: `docs/DECISION_LOG.md` line 31; `docs/REPORT_VIRGIN_6PAGE.md` §5):

- [ ] Annotator-2 κ: fill the blinded pack `evaluation/virgin/relabel_60_blind.csv`, run `scripts/compute_iaa.py`, adjudicate; then the n=100 groundedness label pack for the V4 judge study (biggest trust upgrade left — human-hours, correctly left to humans)
- [ ] Keyed judge V4: G-Eval anchors, judge≠generator family, double-run (FIX_PLAN R2) — needs a GROQ_API_KEY session
- [ ] Constrained generation A/B (FIX_PLAN R3): citation-before-claim LLM drafts vs template, NLI gate ≥ 0.9
- [ ] Time-split train ≤2017-11-15 / test >2017-11-15 (burst-month slice) + supervised virgin LogReg/MiniLM on human labels
- [ ] Hybrid BM25 + MiniLM + rerank, recall@3 ≥ 0.85 on virgin KB

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contributing

Contributions that keep every number traceable to `evaluation/virgin/*.csv|*.md` are greatly appreciated.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please include: script re-ran (`train_virgin.py` / `run_virgin_eval.py` / `run_virgin_judge.py`), CSV/md diff, and the "What is misleading" note for any accuracy claim. Do not commit keys (`GROQ_API_KEY` env-only).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

Data: Kaggle `thoughtvector/customer-support-on-twitter` (TWCS, `twcs.csv` 2,811,774 rows) under **CC BY-NC-SA 4.0** — Virgin 27,817 outbound / 37,444 inbound pool derived TWCS-strict. Banking77 inspected for intent design only (not training). Code + templates in this repo: see submission target; no separate `LICENSE.txt` shipped — data license governs redistribution of derived data. Research sources logged in `research/research_log.md`.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contact

Submission contact: anurag@hiverhq.com

Project: `C:\Hiver` — Virgin report `docs/REPORT_VIRGIN_6PAGE.md`, decisions `docs/DECISION_LOG.md`, eval `evaluation/virgin/` (`results_human200.csv`, `BASELINE_VS_FINAL.md`, `JUDGE_AGREEMENT.md`, `LLM_JUDGE_30.md`, `SAMPLING_NOTE.md`, `FAILURE_TESTS.md`).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Acknowledgments

* [Best-README-Template](https://github.com/othneildrew/Best-README-Template) — section skeleton followed (title/description, TOC, About, Built With, Getting Started, Usage, Roadmap, Contributing, License, Contact, Acknowledgments)
* [Customer Support on Twitter (TWCS)](https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter) — CC BY-NC-SA 4.0 source data
* PolyAI Banking77 (CC-BY-4.0, intent design reference only)
* scikit-learn / pandas / FastAPI / Next.js / pytest / Streamlit
* Groq API docs (base_url / JSON mode / rate limits) + National Rail / Virgin Delay Repay pages for policy wording (no prices quoted in templates)
* [Img Shields](https://shields.io) — static badges only

<p align="right">(<a href="#readme-top">back to top</a>)</p>
