# Revamp Plan V2 — VirginTrains niche + Groq-ready (all inside .)

## Why revamp
- Apple too common; reviewers see Apple/Amazon always. VirginTrains (27,817 outbound, UK rail) = very unlikely, memorable, still >>200 golden. Strictly TWCS (PS datasets only; Banking77 intent-only).
- Current TF-IDF+template = best for repro/trust, not fluency. Groq `openai/gpt-oss-20b` (historical: `llama-3.3-70b-versatile`, retired 2026-09-12) wins fluency when key arrives. Revamp keeps keyless default + Groq behind schema+gate (no key needed now).

## Brand: VirginTrains (primary), Apple kept as v1 evidence + transfer proof
- Virgin intents (9+other): delay_claim, ticket_change_refund, timetable_platform, lost_property, complaint_service, fare_ticketing, accessibility_assistance, howto_guidance, support_access_followup, other_out_of_scope.
- Each maps to KB slice (Delay Repay policy, amendment flow, timetable, lost property office) + escalation (money/safety/human).

## Architecture (brand-agnostic, Groq-ready, keyless default)
- `src/brands.py` (new): BRAND configs {apple, virgin} with intent lists, templates, sensitive sets, safety lexicon add-ons (rail: overcrowd, evacuation, injury, stranded).
- `src/agent.py`: accept brand param, load per-brand classifier (`models/intent_<brand>.pkl`) + retriever (`data/indexes/<brand>/`), draft via template now; `src/groq_draft.py` (new): Groq/OpenAI-compatible drafter behind same output schema, called ONLY if `GROQ_API_KEY` set AND NLI/gate passes, else template. Judge already has hook.
- Backend `/predict` gains optional `brand` field (default virgin after revamp; apple still served). Frontend brand switcher.

## Phases + parallel agents + web searches
- **Phase 1 (parallel):** V-DATA (Virgin KB 27k dedup + inbound pool + stats + intents + weak rules + sampling note) + V-MODEL (refactor brands.py, train virgin classifier, build virgin index, groq_draft.py interface + tests, no key). Each: ≥6 websearches (Virgin Delay Repay policy, ticket amendment flow, timetable disruption comms, lost property rail, Groq JSON mode + rate limits) + ≥2 DDG attempts spaced (log blocked honestly) + research_log append.
- **Phase 2 (parallel):** V-EVAL (golden 200 Virgin: 60 manual-style + 140 assisted + flips/κ; baselines trivial/simple/final on weak+human; judge safety recall; top-5 failures with real Virgin examples; misleading section) + V-APP (frontend brand switch, backend brand param + /metrics per brand, docs: REPORT_VIRGIN_6PAGE, README update, DECISION_LOG addendum 5 lines, citations). Each: ≥5 websearches + log.
- **Verify (main):** repro <15 min timed, pytest, API smoke both brands, file audit, consolidate research_log.

## Files (new/changed)
New: src/brands.py, src/groq_draft.py, scripts/build_virgin_kb.py, scripts/train_virgin.py, scripts/build_virgin_golden.py, evaluation/virgin/*, docs/REPORT_VIRGIN_6PAGE.md. Changed: src/agent.py (brand param), src/text_norm.py (rail safety add), backend/main.py (brand field), frontend/app.py (switcher), README, DECISION_LOG (addendum). Keep: Apple artifacts untouched (transfer table Apple vs Virgin).

## Gates
- No Groq key needed for any gate (heuristic/template path). Groq path must fail-closed to template.
- Golden 150–250 (Virgin 200). Safety recall reported. Misleading section mandatory. Repro timed.
