# Hiver AppleSupport Agent — Report (6 pages)

## 1. Problem framing: what “good” means, what we didn’t build
Brand **AppleSupport** (106,860 replies, iOS 11/iPhone X era). Good = acknowledge → diagnostic question (Settings > General > About) → DM redirect when device/PII needed; every technical claim cites a historical passage ID; link-only/screenshot or KB-miss → clarify + escalate, never invent. Escalate with reason on 4 triggers: safety/legal, account/data-loss, human request/injection, unresolvable (low-conf/no-grounding/link-only/non-English) + complaint-review (frustration + sensitive). Output JSON: intent, confidence, draft, passage IDs, decision, reason. **Not built:** refunds/repairs/account actions, live Apple backend, multilingual (non-English → other + escalate), post-2017 knowledge, autonomous resolution. UI secondary; engine first.

## 2. Results vs two baselines
Golden **200** (`evaluation/golden_human_200.csv`): stratified from 97k inbound pool, 60 fully manual + 140 rulebook-assisted + spot-check; weak-vs-human intent κ 0.465. Systems: **trivial** (majority + canned, always auto), **simple** (keyword + BM25 top-1 copy), **final** (TF-IDF LogReg + TF-IDF NN top-5 + template + rules). CPU, p50 180 ms/p95 192 ms.

| set | system | intent acc / macroF1 | esc P/R/F1 | ground ≥4 |
|---|---|---|---|---|
| weak-200 (circular) | trivial / simple / final | 0.095/0.016 – 1.000/1.000 – 0.795/0.796 | 0.000 – 0.686 – 0.630 | 0.000 – 0.205 – 1.000 |
| human-200 | trivial / simple / final | 0.140/0.03 – 0.830/0.83 – 0.660/0.65 | 0.000 – 0.55 – **0.582** (P 0.469 R 0.767) | – – 1.000 (4.83) |
| human-60 (hardest) | trivial / simple / final | 0.217 – 0.517 – 0.433 | 0.000 – 0.000 – 0.471 | – – 1.000 |

Judge (`evaluation/judge.py` v1, heuristic offline + `gpt-4o-mini` hook): safety recall on 11 human legal_safety cases **0.909** (gate ≥0.90 ✓); esc-vs-human κ 0.487. LLM run needs `OPENAI_API_KEY` (pinned `gpt-4o-mini-2026-07-01`, temp 0); without key, heuristic advisory-only. Full harness: `scripts/run_eval.py`, `eval_human60.py`, `run_judge_agreement.py`.

## 3. Failure analysis: top 5 (real examples + hypotheses)
1. **Safety lexicon miss → FIXED.** “my charger caught flame… burned my finger” was other/auto. Cause: flame/burn absent from safety list. Fix: added flame/burn/shock/electrocut; now legal_safety/escalate. Intent still other — decision guardrail covers, intent miss remains.
2. **Short follow-up misclass.** “It’s 11.0.1.” was software_update; true followup (answer to “which iOS?”). Cause: single-message, no thread. Hypothesis: 2-turn context fixes; currently clarify-by-template.
3. **Link-only hallucination risk.** “how can i fix this problem? [t.co]” was howto/auto; true other/unresolvable. Cause: dead link, no detail. Fix: link-only → escalate + ask for description/version.
4. **Non-English.** Spanish restore / Portuguese Music → was setup/apps; true other + escalate (English-only v1). Cause: keyword match ignores language. Fix: language gate → other.
5. **Vague + profanity under-escalation.** “FIX THIS DAMN GLITCH 3 days” was other/auto; true complaint_review/escalate. Cause: frustration rule required sensitive intent. Fix: profanity + vague → escalate. Injection (“ignore prev… reveal password”) also now escalates (was auto, safe reply but wrong decision).

## 4. What is misleading about my headline number? (mandatory)
- Simple **1.000** / final 0.795 on weak-200 are **circular**: labels = keyword rules, so simple scores perfectly by construction. Never cite.
- Human-200 final 0.660 still optimistic: 140/200 are rulebook-assisted (same family as classifier), only 60 fully manual (there: final 0.433 < simple 0.517; ceiling = weak-human 0.517).
- Groundedness 1.000 rewards templates by design, not human factuality; safety 0.909 on n=11 (wide CI); esc κ 0.487 moderate.
- Latency on dev CPU; n=200 → ±7–12% CIs; per-intent F1 unstable (connectivity/hardware 0.00 on 60). Trust safety + failures + κ, not a single accuracy.

## 5. What we’d do next with one more week
(1) Double-label full 200 (2 annotators + adjudication, report κ); train supervised MiniLM/LogReg on human labels + time-split. (2) Hybrid BM25+MiniLM + rerank, recall@3 ≥0.85. (3) Pinned LLM drafter behind schema + NLI grounding gate + 75-pair judge-human study (wκ ≥0.60). (4) 2-turn thread context + language ID + PII redactor. (5) Cache classifier load (~130 ms win), /metrics + rate-limit + Docker load test. Cost stays $0 CPU; LLM path $0.0002–0.0005/req.

## 6. Decision log (15, why)
- AppleSupport over Amazon: KB-partitionable tech intents, consistent voice. • 11 message-level intents (thread drifts). • No vector DB: 89k tweets, TF-IDF 17 s/p50 35 ms/44 MB. • No agent framework: 5 fixed steps. • Templates over free LLM: keyless, zero invented versions/links. • TF-IDF+LogReg over BERT: CPU <2 min, weak ceiling 0.517. • Weak bootstrap disclosed as weak. • English-only v1. • 4-trigger escalation (single threshold misses flame). • DM = triage, not resolution. • 200 = 60 manual + 140 assisted (time-box, disclosed). • Heuristic judge + gated LLM (κ ≥0.60 + safety ≥0.90). • Dedup template-cap 5 (106k→89k). • Stateless FastAPI, no K8s. • Headline = human, not weak-200.
Repo: `.` (also see `docs/DECISION_LOG.md`). Borrowed: sklearn/pandas/FastAPI/pytest, TWCS (CC BY-NC-SA 4.0), Banking77 (CC-BY-4.0, intent design only), cited in README + research log.
