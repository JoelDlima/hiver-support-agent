# Decision Log — 15 non-obvious decisions (Hiver AppleSupport)

1. **Brand = AppleSupport, not AmazonHelp** (largest Amazon 169k vs Apple 106k). Apple intents partition by KB slice (battery/update/iCloud), Amazon intents diffuse (orders/refunds need PII). Apple voice consistent → template grounding works.
2. **11 intents (10+other), message-level, not thread-level.** Threads drift (follow-up “It’s 11.0.1” ≠ update issue). Single-label + secondary note; multi-intent rate to measure, revisit if >15%.
3. **No vector DB (no Pinecone/Qdrant).** 89k short tweets: sklearn TF-IDF NN builds 17s, p50 35ms, 44MB. Managed DB adds cost/latency without recall gain. Revisit at >1M docs or multilingual.
4. **No agent framework (no LangChain/Graph, LlamaIndex, CrewAI).** Fixed 5-step pipeline; agents compound error (0.95¹⁰≈0.60), break repro. Plain Python + Pydantic dataclass.
5. **Template-grounded replies, not free LLM generation.** No API key in repro, zero hallucinated iOS versions/links, groundedness heuristic 4.75/5. LLM only as optional drafter behind same schema (future).
6. **TF-IDF+LogReg for intent, not fine-tuned BERT.** CPU <2min, 0.945 weak-train acc, interpretable. MiniLM/BERT deferred until human labels >500 (weak-label ceiling 0.517, bigger model just memorizes keywords).
7. **Weak keyword bootstrapping, explicitly labeled as weak.** Needed to start without labels; disclosed circularity (simple 1.0). Human-60 flips=39 prove keywords ≠ truth.
8. **English-only v1; non-English → other + escalate.** ES/PT 800+ rows; translating-and-guessing unsafe. Covers iOS-era cutoff (no post-2017 knowledge).
9. **Four-trigger escalation, not single confidence threshold.** can't-ground / policy-risk / frustration / human-request. Single threshold misses flame/burn (fixed post-smoke-test) and over-escalates short thanks.
10. **DM-deflection treated as triage, not resolution.** 45%+ outbound contain DM; deflection-only passages never ground technical claims. Prevents evasion learning.
11. **Golden 200 weak + 60 human-reviewed, not 200 human.** Time-box: 200 stratified weak for coverage, 60 blind-reviewed for trust (κ reported). Full 200-human is week-2 work.
12. **Judge = heuristic (offline) + LLM hook, not LLM-only.** Heuristic groundedness/actionability runs offline; LLM judge version-pinned, needs wκ≥0.60 + safety-recall≥0.90 to ship, else advisory. Avoids correlation≠agreement trap.
13. **Dedup + template-cap K=5 in KB.** 106k→89k; 1.45% exact duplicates (canned “DM us”). Prevents retrieval collapse to same template.
14. **Stateless FastAPI + SQLite/joblib + LRU, no K8s/Redis.** p50 180ms/p95 192ms on 2vCPU, $6–50/mo to 10k users. Scale via workers → replicas → ANN only on metric triggers.
15. **Report headline = human-60, not weak-200.** Weak-200 simple 1.0 is misleading; human-60 final esc_F1 0.424 + ground 1.0 is the trust claim. “Misleading number” section mandatory in every results print.

## Addendum — Virgin revamp V2 (Phase 2 V-APP, 2026-09-10)

16. **Why VirginTrains primary (not Apple-only):** Apple/Amazon are reviewer-common; Virgin (27,817 outbound, UK rail Delay Repay) is memorable yet still >>200 golden, TWCS-strict (PS datasets only); Apple kept as v1 evidence + transfer proof, not deleted.
17. **Brand-agnostic dict (`src/brands.py`), not forked pipelines:** per-brand {intent_module, model_path+legacy fallback, index_dir+legacy fallback, sensitive/money sets, safety add-ons} + `DEFAULT_BRAND=virgin`; agent/backend/frontend all normalize unknown→virgin so Apple path preserved exactly.
18. **Groq-behind-gate, fail-closed to template (`src/groq_draft.py`):** keyless default; Groq `openai/gpt-oss-20b` (historical: `llama-3.3-70b-versatile`, retired 2026-09-12) via `GROQ_API_KEY` + `base_url=https://api.groq.com/openai/v1` + JSON-schema `{draft_reply}` only if key set AND ≤280 chars AND £/HH:MM grounded, else template (reason `no-key|no-client|validation-fail|error` in signals; UI/API show `draft_path|groq_reason`).
19. **Rail safety add-ons, not base lexicon edit:** `overcrowd/evacuation/injury/stranded/stampede/derail` live in brand config + `virgin_intents.SAFETY_ADDONS` and OR into `legal_safety` at decision time; base `text_norm` untouched so Apple safety behavior unchanged.
20. **Money-intent escalation per brand, not single threshold:** Apple `purchase_billing_service` vs Virgin `delay_claim/ticket_change_refund/fare_ticketing` each gate at conf<0.70 + money signal (£/refund); delay↔amendment overlap dual-flagged in golden (V-EVAL) so arguable intent still escalates correctly.

## Addendum — post-freeze keyword fixes (2026-09-11, private working repo)

21. **Amend cues outrank `lost my` (F7 fix):** added `reprint/reissue/receipt/at the station/duplicate ticket` to `ticket_change_refund` KEYWORDS + `reprint/reissue/receipt` to money-word triggers. Longest-match + dict order does the ranking — no serving-order special case. Rejected: intent→money-gate coupling change (wider blast radius).
22. **`still running` timetable keyword (F2 fix):** bare "still running?" without "running on time" missed timetable. One keyword + retrain fixed it (0.896 other → 0.594 timetable). Rejected: embedding similarity (needs torch, breaks CPU repro).
23. **Crowd remap, not classifier surgery (F4a fix):** LogReg couldn't learn `packed→complaint` from sparse weak labels, so `CROWD_REMAP_TOKENS` remaps other-predictions with conf<0.6 to complaint (capped 0.55). Narrow by design — can never steal delay/refund/timetable. Revisit when human labels >500 allow supervised training.
24. **Weak-200 simple 0.975 disclosed, not re-frozen:** keyword rules changed after `golden_v1.csv` froze, so simple (post-fix rules) scores 0.975 on pre-fix labels. Rebuilding golden to restore 1.000 would destroy the before/after evidence — kept frozen + disclosed.
25. **Mined slices are coverage, not recall:** `mine_safety_slice.py` safety 1.000 (n=20) / money 0.575 (n=40) reported as escalation rates on unlabelled regex-mined candidates, never as recall. Human-labelled recall stays safety n=3 / money n=20.

## Addendum — keyed LLM-judge study (2026-09-11, Groq key via env only)

26. **LLM judge tested against its own gate, kept advisory:** Groq qwen temp-0 n=30 vs blind human grades → verdict κ=0.253, groundedness wκ=0.060, failing the wκ≥0.60 ship gate. Published in `evaluation/virgin/LLM_JUDGE_30.md` with the failure analysis (LLM conflates relevance/groundedness; rubric formula lets wrong-intent drafts pass at 3.55). Rejected: hiding the study because it "failed" — the gate working is the proof.
27. **Reverted the heuristic relevance gate:** `rel<=2 → FAIL` on the heuristic keyed on other-predictions and anti-correlated with human judgment (κ=-0.297 — it failed reasonable triage). Relevance gating needs a genuinely graded signal (LLM rel distribution 1–5); there it proved redundant (0/30 changes). Heuristic code restored with the experiment documented in-code.

## Addendum — balanced retrain + PII/DR30 + judge v2 (2026-09-11, keyed)

28. **`class_weight=balanced` instead of oversampling code:** accessibility had 167/30000 weak hits and F1 0.500. One sklearn arg → tail F1 0.848 (matches simple), headline 0.795/0.803 beating simple on intent too. Rejected: hand-rolled duplication (same effect, more code, seed-sensitive).
29. **PII gate before human_request + DR30 bands in delay template:** `has_pii` (UK phone/email regex on raw text — normalize masks mentions) → `pii_review`; F3b now fires on the number itself. Delay template states DR30 bands hedged ("typically") + booking-ref ask, ≤280 chars. Both were queued H1/H3 — done, tested, 9/9 probes green.
30. **Judge v2 + Groq A/B, both reported against the gate:** passages + double-run gave self-consistency 1.000 but κ=-0.005 (passages rationalize rather than verify) — gate holds twice. A/B 29/30 live drafts: specificity upgrade only, template stays default. Rejected: claiming either as a win.
31. **Annotator-2 pack generated, not graded:** `annotation_pack_50.csv` (30 spotcheck + 20 fresh seed-11) + builder script. The biggest trust upgrade left is human-hours, correctly left to humans.

## Addendum — independent-audit hardening batch (2026-09-16, no headline change)

32. **Thread-safe offline instead of per-request monkey-patch:** `AppleAgent.handle(..., offline=)` + `groq_draft(..., offline=)` skip the LLM; backend passes the flag through (was: module-global stub swapped per request — concurrent offline+online interleaved). Verified: 75 pytest green, eval re-run bit-identical (0.795/0.803, esc 0.767).
33. **One retriever (`src/brand_retrieval.py`), not three:** backend + Streamlit import the canonical `BrandRetriever`; frozen eval copy kept + documented (repro stability); hybrid base fixed (`src/` first, tuple/str lookup normalized). Rejected: rewriting eval retriever (would fork reported numbers).
34. **Rate-limit the expensive routes, not just /predict:** stream + eval/* + embed2d + groundedness added (5/min/IP); `/logs/stream` got disconnect checks (was: infinite sync loop pinning a worker per tab). Demo pacing documented (429 + `Retry-After: 60`).
35. **Honest /readyz instead of always-True:** probes model+index+retriever files per brand (virgin gates, apple reported) + locked lazy init; Docker HEALTHCHECK moved to /readyz; fixed `mkdir traces.jsonl` dir-bug + missing `evaluation/` copy + `.dockerignore`.
36. **Optional `HIVER_API_KEY` instead of always-open or always-auth:** unset = open loopback demo (tests unaffected); set = review mutations + stream/eval require `X-API-Key` (BFF forwards server-side). Full UUID request IDs + no-overwrite rule; `corrected_intent` allowlisted per brand; envelopes unified to RFC-9457; PII retention documented (queue DB stays raw — humans need it — gitignored + auth-gated).
37. **BFF helpers instead of 23 bare fetches:** `frontend-next/lib/proxy.ts` (`proxyJson` 25s timeout/120s eval, `proxyStream`) — dead backend is JSON 502, never Next 500 HTML. Dead nav now anchors real sections; threshold slider labeled display-filter + actually filters the inbox (was: changed nothing).
