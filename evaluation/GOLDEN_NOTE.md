# Golden sets (updated: 200 = 60 manual + 140 rulebook-assisted; see human_review_200.py; spotcheck_30.csv audit before submit) — sampling & labeling note

- `golden_v1.csv` (200): stratified from `apple_inbound_pool.csv` (~18/intent) via weak keyword labels, seed 7. Columns text,intent,escalate,escalate_reason. **Draft only — weak labels, circular with simple baseline. Do not report as headline.**
- `golden_human_60.csv` (60): random 60 from golden_v1, seed 11, single-annotator blind review (AI as annotator) with flip notes (`human_correct_60.py` FIX dict). 39/60 flipped. Weak-vs-human: intent acc 0.517 κ0.465, esc acc 0.70 κ0.015. **Trustworthy subset — headline source.**
- `human_review_60_draft.csv`: pre-review snapshot for audit.
- Label guide: 11 intents (`src/intents.py`); escalate per 4-trigger (legal_safety incl. flame/burn, account/data-loss, human_request/injection, unresolvable link-only/short/non-English, complaint_review frustration+sensitive, money_threshold). Non-English → other + escalate. Link-only → escalate. Safety > intent: escalate even if intent uncertain.
- Limitations: single annotator, n=60 wide CIs, no inter-annotator κ yet. Next: double-label 60 + full 200-human + adjudication.
- Judge agreement: heuristic judge runs offline; LLM judge gated (needs wκ≥0.60 + safety-recall≥0.90 on 60). Current heuristic vs human not yet κ-scored — week-2 (75-pair blinded).
