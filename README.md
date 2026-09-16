<a id="readme-top"></a>

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)](requirements.txt)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=nextdotjs&logoColor=white)](frontend-next/package.json)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688?style=for-the-badge&logo=fastapi&logoColor=white)](backend/main.py)
[![Tests](https://img.shields.io/badge/tests-69%20passing-brightgreen?style=for-the-badge)](tests)
[![Data CC BY-NC-SA 4.0](https://img.shields.io/badge/Data-CC_BY--NC--SA_4.0-lightgrey?style=for-the-badge)](https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter)

<br />
<div align="center">

<h3 align="center">Hiver — VirginTrains Support Agent</h3>

  <p align="center">
    A CPU-only support agent for VirginTrains. It classifies an incoming customer message into one of 10 intents, drafts a reply grounded in how the brand has historically resolved similar issues, and decides whether to auto-handle or escalate — with a stated reason.
    <br />
    The point of the repository is the proof, not the system: golden set, baselines, judge-agreement evidence, failure analysis, and an honest account of what the headline number does not say.
    <br />
    <br />
    <a href="docs/REPORT_VIRGIN_6PAGE.md"><strong>Read the 6-page report »</strong></a>
    <br />
    <br />
    <a href="docs/INDEX.md">Documentation index</a>
    &middot;
    <a href="docs/REPRO.md">Reproduce in 15 min</a>
    &middot;
    <a href="docs/DECISION_LOG.md">Decision log</a>
  </p>
</div>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#results-on-human-200">Results on human-200</a></li>
        <li><a href="#what-the-headline-number-does-not-say">What the headline number does not say</a></li>
        <li><a href="#baselines">Baselines</a></li>
        <li><a href="#judge-agreement">Judge agreement</a></li>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li><a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#repository-layout">Repository Layout</a></li>
    <li><a href="#usage">Usage</a>
      <ul>
        <li><a href="#reproduce-the-headline-in-under-15-minutes">Reproduce the headline</a></li>
        <li><a href="#run-the-service">Run the service</a></li>
        <li><a href="#run-the-demo-ui">Run the demo UI</a></li>
        <li><a href="#optional-live-llm-drafts">Optional: live LLM drafts</a></li>
      </ul>
    </li>
    <li><a href="#changelog">Changelog</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

## About The Project

The agent takes one customer message and returns three things:

1. **Intent** — one of 10 VirginTrains categories (`src/virgin_intents.py`).
2. **Grounded draft** — a template reply (≤280 chars) assembled from retrieved historical resolutions, with no invented prices, times, or URLs.
3. **Triage decision** — `auto_handle` or `escalate`, with a machine-readable reason.

AppleSupport is retained as v1 evidence and transfer proof: the same pipeline serves it, but VirginTrains is the brand this work is built and evaluated around.

10 Virgin intents:

`delay_claim, ticket_change_refund, timetable_platform, lost_property, complaint_service, fare_ticketing, accessibility_assistance, howto_guidance, support_access_followup, other_out_of_scope`

**Corpus** (source: [`docs/REPORT_VIRGIN_6PAGE.md`](docs/REPORT_VIRGIN_6PAGE.md) §1): 27,817 outbound / 37,444 inbound pool derived from TWCS (union ≈65.3k rows pre-dedup; exact union varies by dedup strategy, see the strata sum in [`evaluation/virgin/SAMPLING_NOTE.md`](evaluation/virgin/SAMPLING_NOTE.md)). Retrieval index: 27,172 documents, 19,898 features, build ~0.5–0.6 s, p50 ~7–8 ms / p95 ~8–9 ms on a dev CPU (`data/indexes/virgin/index_meta.json`; the ablation reports 7.1/8.2 ms for the same arm — same order of magnitude, machine-dependent).

### Results on human-200

Golden set: [`evaluation/virgin/golden_human_200.csv`](evaluation/virgin/golden_human_200.csv) — 200 hand-checked examples (60 manually labelled, 140 rulebook-assisted), stratified from the 37,444-message inbound pool with seed 7 and rare-intent oversampling. Weak-label vs human agreement: **acc 0.795, κ 0.772**.

| System | Intent acc / macroF1 | Escalation P / R / F1 | Groundedness mean / ≥4 rate |
|---|---|---|---|
| trivial — canned reply, never escalates | 0.075 / 0.014 | 0.000 / 0.000 / 0.000 | 3.00 / 0.000 |
| simple — keyword rules + retrieval top-1 | 0.790 / 0.796 | 1.000 / 0.135 / 0.238 | 2.33 / 0.015 |
| **final — TF-IDF LogReg + NN k=5 + templates + rules** | **0.795 / 0.803** | **0.778 / 0.757 / 0.767** | **4.21 / 0.900** |

Source: [`evaluation/virgin/results_human200.csv`](evaluation/virgin/results_human200.csv) and [`BASELINE_VS_FINAL.md`](evaluation/virgin/BASELINE_VS_FINAL.md) §B.

**Final − simple on human-200: accuracy +0.005, macroF1 +0.007, escalation F1 +0.529.** The accuracy delta is inside noise; the escalation delta is the real result. A balanced `class_weight` retrain fixed the accessibility tail (F1 0.500 → 0.848) and the final system matches or beats simple on 9 of 10 per-intent F1 scores, trailing only `delay_claim` (source: [`BASELINE_VS_FINAL.md`](evaluation/virgin/BASELINE_VS_FINAL.md) §C).

### What the headline number does not say

The 0.795 accuracy is **+0.005 over a keyword-rule baseline — statistically indistinguishable from it**. Anyone quoting 0.795 as evidence that the classifier "works" is over-reading it. The honest claims in this repository are:

- The **escalation decision** is where the modelling pays off (+0.529 F1), because keyword rules escalate almost everything (recall 0.135).
- The golden set is **single-annotator**, so κ 0.772 measures agreement with one person, not with a population. The blinded relabel pack and `scripts/compute_iaa.py` exist to fix this; they need one human hour.
- A separate weak-200 evaluation reports 0.970–0.975 accuracy, but its labels were frozen using pre-fix keyword rules, so it is **circular by construction** and must not be cited as a headline (source: [`BASELINE_VS_FINAL.md`](evaluation/virgin/BASELINE_VS_FINAL.md) §A).
- An honest pre-fix-vs-final reconstruction (`scripts/r1_prefix_baseline.py`) puts the true keyword-teacher delta at **+0.020 accuracy, CI [−0.035, +0.080]** — still noise — with **+0.572 escalation F1** (source: [`evaluation/virgin/R1_PREFIX_BASELINE.md`](evaluation/virgin/R1_PREFIX_BASELINE.md)).
- A miss audit buckets all 41 human-200 errors: **41% out-of-scope/noise, 27% genuinely ambiguous, 29% model error** — i.e. only about 12 of 200 are real capability failures (source: [`evaluation/virgin/MISS_AUDIT.md`](evaluation/virgin/MISS_AUDIT.md)).

The full discussion is §4 of the [6-page report](docs/REPORT_VIRGIN_6PAGE.md).

### Baselines

- **trivial** — majority-class intent plus a canned reply; never escalates.
- **simple** — Virgin keyword rules (post-fix) plus retrieval top-1 copied through.
- **final** — TF-IDF + LogReg intent model (`models/intent_virgin.pkl`, trained on 30k weak labels with `class_weight=balanced`), Virgin TF-IDF nearest-neighbour retrieval at k=5, Virgin templates (Delay Repay bands), and brand-aware triage triggers (rail safety add-ons, money intents, crowd remapping, PII gate).

### Judge agreement

Ship gate is `weighted κ ≥ 0.60` **and** safety-recall ≥ 0.90. It is currently **advisory only**, because the evidence does not clear it — and that is reported rather than hidden (source: [`evaluation/virgin/JUDGE_AGREEMENT.md`](evaluation/virgin/JUDGE_AGREEMENT.md)):

| Check | Result |
|---|---|
| Escalation vs human | acc 0.915, κ 0.715 |
| Safety recall (`legal_safety`, n=3) | 1.000 — tiny sample, CI ≈0.4–1.0, **not claimable** |
| Money recall (`money_threshold`, n=20) | 0.850 |
| LLM judge v1 (no passages) | verdict κ 0.253, groundedness wκ 0.060 → gate holds |
| LLM judge v2 (passages + double run) | verdict κ −0.005, self-consistency 1.000 → gate holds |
| LLM judge v3 (claim-level, heuristic leg) | wκ 0.007 → **gate FAIL, reported honestly** |

Failure probes (source: [`evaluation/virgin/FAILURE_TESTS.md`](evaluation/virgin/FAILURE_TESTS.md)): 9 exact-text probes re-run post-fix → **9 PASS / 0 PARTIAL / 0 FAIL**, with regression coverage in `tests/`.

### Built With

* **Python 3.12** — `numpy==2.5.3`, `pandas==3.0.5`, `scikit-learn==1.9.0` (TF-IDF + LogReg intent, nearest-neighbour retrieval), `scipy==1.18.1`, `joblib==1.6.0`
* **FastAPI `0.141.1`** + `uvicorn==0.52.4` — `backend/main.py`, 26 routes across prediction, judging, evaluation, review, and telemetry
* **Next.js 14** + React 18 + three.js / `@react-three/fiber` + Tailwind — demo UI in `frontend-next/` with 22 BFF proxy routes
* **Streamlit `1.63.0`** — legacy single-file demo, `frontend/app.py`
* **pytest `9.1.1`** + `httpx` — 69 tests in `tests/`
* **Groq** (optional) — live drafter behind a validation gate, fail-closed to templates

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

Everything runs on CPU. **No API key is required for any headline number** — the drafter fail-closes to deterministic templates when `GROQ_API_KEY` is unset, so a keyless run is reproducible.

Commands below are written for PowerShell on Windows. The Python commands are path-neutral and work from any shell (including bash on macOS/Linux) once the virtual environment is active; only the venv activation line differs.

### Prerequisites

* Python 3.12 (`py -3.12` on Windows)
* Node.js ≥ 18.17 and npm — only needed for the demo UI
* Git
* Optional, for live LLM drafts: `GROQ_API_KEY` in the environment (never in code or logs)
* Optional, only for a full data rebuild: `pip install kagglehub`, then download `thoughtvector/customer-support-on-twitter` and place `twcs.csv` at `data/raw/twcs.csv` (this file is gitignored; the frozen-artifact path below does not need it)

### Installation

Run everything from the repository root.

```powershell
# 0. Virtual environment (once)
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1          # bash/zsh: source .venv/bin/activate
pip install -r requirements.txt

# 1. Verify the checkout
python -m pytest tests -q
```

The Python interpreter that runs `tests/` and the `scripts/` commands needs the repository root on its import path — the test suite is configured for this, and for standalone scripts set `PYTHONPATH` to the repository root (or simply run them from it).

```powershell
$env:PYTHONPATH="."                 # bash/zsh: export PYTHONPATH=.
```

**Optional — rebuild every artifact from raw data** (~6–8 min on CPU; needed only if you want to regenerate models and indexes rather than use the committed ones):

```powershell
python scripts\build_virgin_kb.py        # -> data/processed/virgin_kb.csv (27,172 records) + inbound pool (37,444)
python scripts\build_virgin_index.py     # -> data/indexes/virgin/ (TF-IDF nearest-neighbour index)
python scripts\train_virgin.py           # -> models/intent_virgin.pkl
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Repository Layout

```text
.
├── README.md                  # this file (the only README)
├── requirements.txt
├── pytest.ini
├── src/                       # agent core: normalisation, intents, classifier, retriever, drafts, agent
├── backend/main.py            # FastAPI service (26 routes)
├── frontend-next/             # Next.js 14 demo UI + BFF proxy routes
├── frontend/app.py            # legacy Streamlit demo (single file)
├── scripts/                   # build, train, evaluate, and study runners
├── tests/                     # 69 tests, including failure-probe regressions
├── models/                    # trained intent model
├── data/                      # processed KB, inbound pool, retrieval index (raw TWCS is gitignored)
├── evaluation/                # the evidence: golden set, results CSVs, baselines, judge agreement
├── eval_providers/            # judge-provider adapter
├── deployment/                # Dockerfile + build context notes
└── docs/                      # all documentation
    ├── INDEX.md               # index of everything below
    ├── REPORT_VIRGIN_6PAGE.md # the report
    ├── DECISION_LOG.md
    ├── REPRO.md
    ├── ANNOTATION_PROTOCOL.md
    ├── research/              # research trail: notes, paper digests, technology decisions
    ├── plans/                 # internal execution plans
    ├── reviews/               # self-audits and positioning
    └── archive/               # superseded AppleSupport-era reports
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

### Reproduce the headline in under 15 minutes

Models and indexes are committed, so the headline numbers come from two commands (~1 minute total):

```powershell
python scripts\run_virgin_eval.py    # -> evaluation/virgin/results_human200.csv + BASELINE_VS_FINAL.md
python scripts\run_virgin_judge.py   # -> judge-agreement inputs
python -m pytest tests -q            # 69 tests, including the failure-probe regressions
```

Full instructions, timings, and the rebuild alternative are in [`docs/REPRO.md`](docs/REPRO.md).

### Run the service

```powershell
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

```powershell
# Classify, retrieve, draft, and triage one message
curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d "{\"text\":\"my train from Euston was delayed 45 mins, how do I claim Delay Repay?\",\"brand\":\"virgin\"}"

# Liveness vs readiness (readiness probes each brand's artifacts)
curl http://127.0.0.1:8000/healthz
curl http://127.0.0.1:8000/readyz
curl http://127.0.0.1:8000/metrics
```

`/predict` returns `intent`, `intent_confidence`, `draft_reply`, `grounding_passage_ids`, `decision`, `escalate_reason`, and per-stage latency. `POST /predict/stream` returns the same pipeline as server-sent events.

### Run the demo UI

```powershell
cd frontend-next
npm install
$env:FASTAPI_URL="http://127.0.0.1:8000"     # bash/zsh: export FASTAPI_URL=http://127.0.0.1:8000
npm run dev                                   # http://localhost:3000
```

The UI has three tabs. **Try it** runs the live pipeline and shows per-stage latency, confidence, grounding passages, and the escalation reason. **Proof** shows the evaluation evidence and the readability/retrieval views. **Review** is the human-in-the-loop inbox (enqueue, approve, edit, reject, transfer) with a full audit trail.

Use any free port — set `-p <port>` on `next dev` if 3000 is taken. Also run the backend, since the UI proxies to it through its BFF layer; a dead backend surfaces as a JSON 502 rather than a broken page.

### Optional: live LLM drafts

```powershell
$env:GROQ_API_KEY="gsk_..."    # never commit this; never log it
```

With a key set, the drafter calls Groq (`openai/gpt-oss-20b`, temperature 0) and validates the output before use. It is fail-closed: `no-key`, client error, timeout, or a validation failure (too long, or an ungrounded price/time/URL) falls back to the template. Responses always report `draft_path` (`template` | `groq`) and `groq_reason`, so the provenance of any draft is explicit. The free tier is roughly 30 requests/minute, so the model is never on the critical path and never used in bulk during evaluation.

### Configuration

| Variable | Default | Purpose |
|---|---|---|
| `FASTAPI_URL` | `http://127.0.0.1:8000` | Backend URL used by the Next.js BFF layer |
| `GROQ_API_KEY` | unset | Enables live LLM drafts; unset keeps the deterministic template path |
| `HIVER_OFFLINE` | unset | Set to `1` to force template-only drafts with no outbound calls |
| `HIVER_API_KEY` | unset | Optional shared secret. When set on both services, mutating and expensive routes require it. Leave unset for the open loopback demo |
| `HIVER_TRACES_PATH` | `data/traces.jsonl` | Where request traces are written |
| `HIVER_REVIEW_DB` | `data/processed/review_queue.db` | Where the human-review queue persists |

Rate limits: `/predict`, `/predict/stream`, `/review/enqueue`, `/eval/*`, `/embed2d`, and `/judge/groundedness` are limited to 5 requests/minute per IP (429 with `Retry-After: 60`). Pace manual demo traffic accordingly.

Privacy note: review-queue and inspect payloads retain raw customer text because human triage needs it. Treat that database as runtime PII state — it is gitignored, and it should be retained briefly and never published.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Changelog

### V3 — hardening and repository hygiene (2026-09-16)

* **Correctness**: thread-safe offline flag through the request handler and drafter (replacing a per-request monkey-patch); unified stream token budget; single canonical retrieval module shared by the backend and the Streamlit demo.
* **Operational honesty**: `/readyz` now probes each brand's artifacts instead of trusting a client that fail-closes and therefore never raises; Docker `HEALTHCHECK` targets it.
* **Input safety**: corrected-intent allowlist, Pydantic field caps, RFC 9457 error envelopes, full-UUID request IDs, async log streaming with disconnect checks.
* **Security**: optional `HIVER_API_KEY` gate that the BFF forwards server-side, so browser clients never hold the secret.
* **Frontend**: all 22 proxy routes funnel through one helper, so an unreachable backend yields a JSON 502 rather than unhandled HTML; fixed a streaming bug where Next.js cached `fetch` GETs and buffered an infinite SSE body forever, hanging the live-log route.
* **Repository**: removed ~1,000 files of vendored third-party tooling and generated artifacts so a clone contains the project itself; documentation consolidated under `docs/` with a single README; all absolute machine paths in code and docs replaced with repo-relative ones.

### V2 — proof workstreams (2026-09-15)

Verified end-to-end at the time: 75 pytest (since trimmed to 69 with the removal of artifact-specific tests), `npm run build`, and a live smoke of every endpoint plus the full review loop.

* **New endpoints**: `POST /judge/groundedness` (claim-level entailment, deterministic offline fallback), `POST /eval/retrieval-ablation` (8 arms), `GET /eval/compare` (file-cached brand matrix), and an `offline` flag on `/predict` and `/predict/stream`.
* **Demo restructure**: three-tab UI (`Try it / Proof / Review`) with zod-validated live payloads; the 3D graph and log tail moved under Advanced.
* **Honest baseline**: pre-fix keyword rules reconstructed from git history and rescored on human-200 (+0.020 accuracy, +0.572 escalation F1).
* **Miss audit**: all 41 human-200 errors bucketed and documented.
* **Portability**: hardcoded roots removed from code, `requirements.txt` synced with the environment, Dockerfile rewritten for the current entry point, and a blinded double-labelling pack prepared for the inter-annotator study.

### V1 — initial AppleSupport agent (2026-09-11)

The original pipeline and evaluation, retained as transfer evidence for the multi-brand claim.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Roadmap

Done:

- [x] Balanced `class_weight` retrain — accessibility tail F1 0.500 → 0.848
- [x] PII gate (`has_pii` regex → `pii_review`) applied before the human-request path; templates carry no PII slots, so echoing is structurally impossible
- [x] Delay Repay bands in the delay template, hedged and length-capped
- [x] Judge v1/v2/v3 studies reported against the gate, including the failures
- [x] 9/9 failure probes green, with regression tests
- [x] Per-brand `/metrics` and a brand-agnostic configuration layer
- [x] V2 proof endpoints, honest pre-fix baseline, and miss audit
- [x] V3 hardening and repository hygiene

Next — deliberately left open, because each needs either a keyed session or human labelling time:

- [ ] **Inter-annotator agreement (highest value):** fill `evaluation/virgin/relabel_60_blind.csv`, run `scripts/compute_iaa.py`, adjudicate disagreements, and publish the κ appendix
- [ ] **Judge v4:** G-Eval-style anchors, judge family ≠ generator family, double-run — needs a keyed session plus a second labelling pass
- [ ] **Constrained generation A/B:** citation-before-claim drafts against the template baseline, with an entailment gate
- [ ] **Temporal split:** train ≤ 2017-11-15 / test > 2017-11-15, plus supervised training on human labels
- [ ] **Hybrid retrieval:** BM25 + sentence embeddings + reranking, targeting recall@3 ≥ 0.85
- [ ] **Thread-context features:** the classifier never sees prior turns today, even though golden rows carry them

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contributing

Contributions are welcome, provided every number stays traceable to a file under `evaluation/`.

1. Fork the project
2. Create a branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Push and open a pull request

Please include the script you re-ran (`train_virgin.py`, `run_virgin_eval.py`, `run_virgin_judge.py`), the resulting diff, and — for any accuracy claim — the corresponding "what is misleading" note. Never commit keys; `GROQ_API_KEY` is environment-only.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

The dataset is Kaggle [Customer Support on Twitter](https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter) (TWCS, 2,811,774 rows) under **CC BY-NC-SA 4.0**. The VirginTrains corpus here (27,817 outbound / 37,444 inbound pool) is derived from it. Banking77 was inspected for intent design only and is not used for training. No separate `LICENSE.txt` is shipped: the data licence governs redistribution of the derived data, and the research trail with all sources consulted is logged in [`docs/research_log.md`](docs/research_log.md).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contact

Submission contact: anurag@hiverhq.com

Where to look: the [6-page report](docs/REPORT_VIRGIN_6PAGE.md), the [decision log](docs/DECISION_LOG.md), the [documentation index](docs/INDEX.md), and the evidence in [`evaluation/virgin/`](evaluation/virgin).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Acknowledgments

* [Best-README-Template](https://github.com/othneildrew/Best-README-Template) — section skeleton
* [Customer Support on Twitter (TWCS)](https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter) — CC BY-NC-SA 4.0 source data
* PolyAI Banking77 (CC BY 4.0) — intent-design reference only
* scikit-learn, pandas, FastAPI, Next.js, pytest, and Streamlit
* Groq API documentation, and National Rail / Virgin Trains Delay Repay pages for policy wording (no prices are quoted in templates)
* [Shields.io](https://shields.io) — static badges

<p align="right">(<a href="#readme-top">back to top</a>)</p>
