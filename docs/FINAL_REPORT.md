# Hiver Final Report — AppleSupport Twitter Agent (2026-09-10)

## 1. Executive summary
Built deterministic AppleSupport agent (classify 11 intents → retrieve 89k historical replies → template-grounded draft → trigger escalate) in `C:\Hiver`, CPU-only, <15min repro. Trust claim is **human-60**, not weak-200: final intent 0.433/macro 0.443, esc_F1 0.471 vs simple 0.517/0.547/0.000 — final loses intent (weak-label ceiling) but wins safety/escalation + groundedness 1.0 + p50 180ms. All code/data/eval inside `C:\Hiver`.

## 2. Problem interpretation / what “good” means
Good = acknowledge → diagnostic (Settings>General>About) → DM redirect when PII needed; every technical claim cites passage ID; abstain when link-only/KB-miss; escalate safety/account/human/frustration with handoff packet. Not built: autonomous refunds/repairs, account actions, live Apple backend, multilingual, post-2017 knowledge. Message-level intent (drifts mid-thread). See `research/problem/problem_decomposition.md`.

## 3. Dataset analysis
`twcs.csv` 2,811,774 rows; AppleSupport 106,860 outbound, ~97k inbound mention pool. Oct–Nov 2017 burst (iOS11/11.1, iPhone8/X, I→A? bug). Chars mean 123/med 125; URLs 46%, mentions 99.9%, emoji 7%. Threads mean 2.42. Dedup → KB 89,694 (template-cap 5), inbound pool 97,592. Preprocess: NFKC, URL→<URL>, @AppleSupport→<BRAND>, hashtag keep, emoji→<EMOJI>. Time-cutoff frozen 2017. See `research/datasets/data_quality.md`.

## 4-7. Research / existing / landscape / architecture
10 tracks, ~100 searches logged (`research/research_log.md`). Key: ldulcic seq2seq (ungrounded BLEU-only) to beat; Intercom Fin (validate→escalate) to emulate simply; keyword pseudo-labels inflate 99.5% (trap avoided via human-60). Landscape by capability (`research/technology-landscape.md`). Architecture: TFIDF-LogReg + TFIDF-NN + template + rules; no vector DB, no agent framework (see `research/architecture/architecture_decision.md`, `docs/DECISION_LOG.md`).

## 8-12. Model / retrieval / workflow / DB / scale
Model: TFIDF-LogReg (30k weak, 0.945 train-vs-weak). Retrieval: TFIDF-NN 17s build, p50 35ms, top-5 + IDs. Workflow: deterministic 5-step, Pydantic dataclass, ≤2 retries→template. DB: joblib+CSV (SQLite optional). Scale: stateless FastAPI, p50 180ms/p95 192ms end-to-end, $6–50/mo to 10k users; workers→replicas→ANN path. Security: PII-DM redirect, secret block, injection→escalate, fail-close.

## 13. Evaluation methodology
Golden 200 stratified weak-draft + 60 human-reviewed (seed 11, 39 flips; weak-vs-human intent acc 0.517 κ0.465, esc acc 0.70 κ0.015). Metrics: intent acc+macroF1+per-intent, esc P/R/F1 (recall≥0.90 target, not met — see limitations), recall@k diagnostic, heuristic groundedness 1-5 (DM+diagnostic+length+cite), judge-human κ gate (LLM judge deferred, heuristic only). Baselines: trivial (majority+canned) + simple (keyword+BM25 top-1). Failure suite F1–F8 smoke-tested. See `research/evaluation/eval_strategy.md`, `evaluation/rubric.md`.

## 14-16. Baseline / final / ablation
Weak-200: trivial 0.095/0.016/0.0, simple 1.0/1.0/0.686, final 0.795/0.796/0.630, ground 3.0/2.98/4.75. Human-60: trivial 0.217/0.032/0.0, simple 0.517/0.547/0.0, final 0.433/0.443/0.471 (P0.400 R0.571). Ablation (inferred): -retrieval → ground 4.75→~3.0; -rules → esc_F1→~0; -classifier→keyword (simple row); -templates→copy (ground 2.98). No reranker/LLM to ablate v1.

## 17. Failure testing — top 5 (real examples)
1. **Safety miss (FIXED):** “my charger legit caught flame… burned my finger” → was other/auto (flame/burn not in lexicon). Fixed lexicon → legal_safety/escalate. Intent still other — guardrail covers decision, intent miss remains.
2. **Vague glitch:** “FIX THIS DAMN GLITCH 3 f*cking days” → other correct, was auto → now complaint_review/escalate. Shows profanity+low-detail needs escalate.
3. **Link-only:** “how can i fix this problem? [t.co]” → was howto/auto → now other/unresolvable/escalate. Dead links must clarify, not diagnose.
4. **Short follow-up misclass:** “It’s 11.0.1.” → was software_update → human support_access_followup. Thread context needed; single-message loses.
5. **Non-English:** Spanish restore Q / Portuguese Apple Music → was setup/apps → human other/unresolvable/escalate (English-only v1). Translating-and-guessing rejected.
Prompt injection (“ignore prev… reveal password”) now escalates (was auto, safe reply but wrong decision). Empty/huge/link-only all escalate. See `scripts/smoke_fail.py`.

## 18. “What is misleading about my headline number?” (mandatory)
- Simple 1.000 / final 0.795 on weak-200 are **circular**: golden labels = keyword rules, so simple scores perfectly by construction. Do not cite.
- True ceiling = weak-vs-human 0.517 (κ0.465). Final 0.433 is below simple because both train on weak labels; bigger model would just memorize keywords better, not understand better.
- Escalation κ 0.015 shows heuristic labels ≈ random vs human — weak esc numbers meaningless.
- Groundedness heuristic rewards templates (1.0 ≥4 rate) by design; not comparable to human factuality.
- n=60 human → wide CIs (±~12%); per-intent F1 unstable on 5-6 examples/intent. Latency on dev CPU, not prod.
Trust only: human-60 + flips + κ + failure suite. Full 200-human needed for ship.

## 19. Competitive differentiation
Not “GPT+RAG”: thread-aware Apple KB (89k deduped) + intent-conditioned templates with IDs + 4-trigger escalate + dual golden (weak+human) + disclosed circularity + smoke-tested safety fix. No open AppleSupport-Twitter harness reports intent+escalation+groundedness+latency jointly.

## 20. Cost / latency
CPU $0 infer, 180/192ms p50/p95, 44MB index. LLM path $0.0002–5/req est. 100/1k/10k users $6–12/12–25/25–50/mo vs $300–6k LLM-per-request.

## 21. Limitations → next week
Escalation recall 0.50 < 0.90 bar; intent 0.433 < 0.85 bar. Week: (1) label 200-human (double-label 60, adjudicate), train supervised LogReg/MiniLM + time-split; (2) hybrid BM25+MiniLM + rerank, recall@3≥0.85/intent; (3) pinned LLM drafter (json_schema) + NLI grounding gate + 75-pair judge-human study (κ≥0.60); (4) thread context (2-turn) + language ID + PII redactor; (5) FastAPI metrics/cache/rate-limit + Docker compose load test.

## 22. How to run
See `README.md` (7 commands, <15min). API `POST /predict {text}` → `{intent, confidence, draft_reply, grounding_passage_ids, decision, escalate_reason}`. Tests `pytest tests -q` (4 pass). Artifacts: `models/intent_classifier.pkl`, `data/processed/apple_kb.csv`, `data/indexes/`, `evaluation/golden_v1.csv`, `golden_human_60.csv`, `results*.csv`.

## 23. Decision log
15 decisions in `docs/DECISION_LOG.md` (brand choice, no vector DB/framework, template>LLM, 4-trigger, English-only, dual golden, headline=human-60).

## 24. Reproducibility / audit
Fresh dev: README + `requirements.txt` + frozen seeds (42/7/11). No secrets, synthetic PII only, CC BY-NC-SA data. Research log + per-track docs + architecture decision + smoke/failure evidence in repo. “Why better than wrapper?” — grounded IDs + measured escalation + disclosed limits, not claims.
