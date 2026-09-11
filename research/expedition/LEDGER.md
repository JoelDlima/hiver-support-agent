# EXPEDITION LEDGER — Deep Technical Research (2026-09-11/12)

Method: 8 parallel specialist tracks, 112 distinct substantive searches, primary sources only.
No code written. This file is the decision record. SearXNG shallow clone at `C:\Hiver\searxng`
(25.6 MB, 992 files; 4 `:socket` deploy templates unrepresentable on NTFS, see
`C:\Hiver\searxng\WINDOWS_CHECKOUT_NOTE.txt`). Disk free at start: ~148 GB.

## Search count by track (112 total, deduplicated by topic reservation)

| Track | Searches | Core sources |
|---|---|---|
| 1 intent classification | 13 | Banking77/Loukas, SetFit/Tunstall, BERTopic/Grootendorst, DeBERTaV3, BERTweet, Guo/Desai calibration, Liu Energy, DETER, Snell ProtoNet |
| 2 retrieval/RAG | 14 | RRF/Cormack, Elastic hybrid, T2-RAGBench, BEIR/MTEB, FAISS/Qdrant/Chroma/LanceDB benches, HyDE/ReDE-RF, MMR, mtRAG, microblog BM25 |
| 3 LLM generation/grounding | 15 | Groq structured-output docs, Instructor, AlignScore, FENICE, ALCE, FrugalGPT/RouteLLM, Atil determinism, Klaviyo, Rasa rephraser |
| 4 agents/orchestration | 14 | Anthropic effective-agents, DSPy/GEPA, LangGraph, OpenAI Agents SDK, SmolAgents, Haystack, agentic-RAG benchmark, self-correction literature |
| 5 evaluation/statistics | 14 | Zheng MT-Bench, Shi bias survey, Zapf kappa CIs, Dror/Koehn bootstrap, RAGAS/ARES, selective-prediction, Promptfoo/DeepEval/Ragas, contamination surveys |
| 6 observability/MLOps | 14 | OpenInference spec, OpenLLMetry, Phoenix, Langfuse/LangSmith/Helicone pricing, Promptfoo CI, price tables |
| 7 security/safety | 13 | OWASP LLM Top10 2025, NIST AI RMF + GenAI profile, MS SFI spotlighting, Greshake indirect injection, Presidio, promptfoo/garak |
| 8 engineering/UX/deploy | 15 | FastAPI SSE docs, Next.js streaming, React Flow/dagre, DR-methodology surveys, pytest-openapi, Compose vs PaaS, vaporware-detection literature |

Local grounding verified 2026-09-12: venv contains NONE of slowapi/instructor/setfit/
sentence-transformers/bertopic/rank-bm25/faiss/presidio/promptfoo/dspy/langgraph
(only pydantic present) — every adoption is a new dependency and must earn it.
Frontend `page.tsx` shows zero hardcoded-fake signals (all panels fetch live backend routes).

## Ideal architecture (synthesized from tracks)

Deterministic 5-step pipeline (track 4 verdict: 28/28, agents rejected) with:
- Intent: weak-pretrained → SetFit/MiniLM prototype head on 200 gold, temp-scaled,
  MSP/Energy abstention gate; TF-IDF+LogReg retained as baseline arm (tracks 1+5).
- Retrieval: BM25 stage-1 + optional MiniLM dense fused by RRF, metadata pre-filter,
  thread-aware rewrite, evaluated by Recall@5/MRR on 50–200 pairs (track 2).
- Drafting: template default; Groq via Instructor+Pydantic, strict JSON schema,
  deterministic content gate (£/HH:MM/URL allowlist), fail-closed; Ollama local
  fallback for keyless LLM repro (track 3).
- Escalation: rules + calibrated confidence + abstention coverage accounting (tracks 1+5).
- Proof: Promptfoo CI gate + bootstrap CIs + dual-annotator pilot + claim-level
  faithfulness + hardened judge protocol (tracks 5+6).
- Safety: retrieved-content sandboxing + injection suite + rate limits + log scrubbing (track 7).
- Product: React-Flow default graph, PCA/SVD embed, POST-SSE streaming, per-widget
  liveness badges, Compose one-command (track 8).
- Observability: JSONL traces + fingerprinting, no hosted collector (track 6).

## Codebase audit vs ideal (assume-poor-then-verify method)

GREEN (keep, genuinely strong): dual golden + 41-flip log; baselines that beat final on
intent (published loss); circularity/misleading sections; gated judge with TWO published
failed studies; fail-closed Groq + £/HH:MM/URL gate; PII-before-human-request gate; rail
SAFETY_ADDONS + money-any-confidence rule; crowd remap; per-brand metrics + request IDs +
inspect/log-tail/eval-run/embed2d endpoints; live-proxy Next.js routes; 31-entry decision
log; sampling note; regression tests (24 green); Apple-regression caught+fixed (3ba8dbb).

YELLOW (acceptable, improvable): TF-IDF+LogReg (→ SetFit head, keep as baseline);
TF-IDF-NN retrieval (→ BM25+RRF hybrid, needs recall@k); heuristic groundedness
(→ claim-level faithfulness); n=30 judge v1/v2 (→ hardened protocol, n≥100);
3D-first visualization (→ React-Flow default, 3D toggle); pinned-but-drifted
requirements.txt (venv ≠ pins; groq/openai unlisted — FIX); stale docs
(UNIQUENESS.md pre-fix numbers; REPORT_VIRGIN §2 esc 0.845/0.556 + money 0.800 vs true
0.915/0.715 + 0.850 — FIX before submission).

RED (weak/missing, load-bearing): single-annotator 140-assisted labels (weakest method
link); safety slice n=3 (unpowered — correctly gated, still unpowered); NO retrieval
quality metric (Recall@k/MRR unmeasured); NO bootstrap CIs on any delta (+0.005 intent
lead is noise, SE≈0.028 — disclosed, still unquantified in-repo); NO virgin confusion
matrix file; NO rate limiting / retry budget / breaker; NO retrieved-content sandboxing
(T2: raw-tweet KB flows into Groq prompt — highest real security gap); NO adversarial /
injection test suite; NO trace files or prompt/dataset fingerprinting.

GRAY (unnecessary for proof): Streamlit legacy demo (harmless fallback, zero proof value —
keep, do not extend); any future hosted-tracer/vector-DB/agent-framework dependency.

## ADOPT list (worth implementing under take-home constraints)

A. Proof/eval (highest ROI): Promptfoo harness + CI gate; bootstrap CIs + McNemar
everywhere; dual-annotator pilot (pack exists); virgin confusion-matrix CSV;
claim-level faithfulness scorer; Recall@5/MRR retrieval eval; hardened judge
(swap+reference+CoT, different family, n≥100).
B. Model: SetFit/MiniLM-L6 prototype head (gold-finetuned, weak-pretrained), TF-IDF kept
as baseline; temperature scaling + MSP/Energy abstention with coverage reporting;
BERTopic offline taxonomy audit (report-only); verify TweetNormalizer parity.
C. Retrieval: rank_bm25 + RRF hybrid (flag-gated, ship only on measured delta);
metadata pre-filter; thread-aware rewrite; MiniLM dense optional; reranker flag-only.
D. Generation: Instructor+Pydantic Groq path (retries 1–2, fail-closed mapping);
strict:true where supported; Ollama fallback for keyless LLM repro.
E. Orchestration: keep deterministic pipeline; per-step Pydantic schemas + gates;
DSPy-style eval-driven tuning pattern (no dep); hand state-machine only for HITL demo.
F. Observability: JSONL traces (OpenInference-compatible keys, no collector);
prompt/model/dataset sha fingerprinting; /metrics counters; Promptfoo CI gate.
G. Security: <UNTRUSTED-TWEET> sandboxing; URL allowlist + £/time sanity; 20-payload
injection suite in Promptfoo; slowapi + tenacity + pybreaker; scrubadub log scrubber;
gitleaks pre-commit; LLM_ENABLED kill-switch; provenance line in UI.
H. Product: React-Flow+dagre default graph (3D toggle); keep SVD embed2d, label
method+seed; POST-SSE via fetch+ReadableStream; skeleton/Suspense/error states;
pytest-openapi contract test; docker compose one-command; seed file + make targets;
per-widget liveness badges (request_id, ms, tok/s).

## REJECT list (complexity without proof value)

Vector-DB servers (Qdrant/Milvus/Weaviate/pgvector) at 27k docs; LLM rerankers default-on;
HyDE default-on; LoRA/fine-tuning for tone; per-request NLI/citation pipelines;
LiteLLM proxy+Redis; vLLM GPU servers; multi-sample conformal abstention;
multi-agent frameworks (CrewAI/AutoGen); full ReAct autonomy; LangChain chains;
NeMo Guardrails / llm-guard (archived) / Rebuff inline; Presidio inline (regex first,
Presidio conditional); hosted tracers as required deps; MLflow server / W&B / DVC;
HELM / lm-eval-harness as primary harness; full triple annotation; t-SNE default;
3D-as-primary; native EventSource for POST; Streamlit-only demo; SSE streaming on the
Groq structured-output path (provider-forbidden).

## Unresolved (need humans/keys, not more searches)

1. Fresh-venv repro from pinned requirements (pins currently drifted from venv).
2. Annotator-2 hours for the 50-pack (biggest trust upgrade, correctly human work).
3. Groq key availability for any n≥100 judge rerun (free-tier 429 risk).
4. Confirm node_modules/.next not tracked by git (present on disk; check before submit).
