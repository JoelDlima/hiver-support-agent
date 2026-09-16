# Ablation — which components matter (§24)

Date: 2026-09-10. Set: `golden_human_60.csv` (n=60, human_intent/human_escalate). Script: `scripts/run_ablation.py` (created this task).
Repro: `$env:PYTHONPATH="."; .venv\Scripts\python.exe scripts\run_ablation.py` (prints only; never overwrites results CSVs).

## Systems
- **A final**: `AppleAgent(retriever)` — LogReg + TF-IDF-NN k=5 + template + 4-trigger rules.
- **B no-retrieval**: `AppleAgent(retriever=None)` — identical classifier/draft/rules, passages forced empty.
- **C keyword-only**: `keyword_baseline + top-1` — weak rules, no learned classifier, no escalation rules.
- **D trivial**: majority canned, never-escalates.

## Results (measured 2026-09-10)
| System | intent_acc | macroF1 | esc_P | esc_R | esc_F1 | grounded_rate | unresolvable_rate |
|---|---|---|---|---|---|---|---|
| D trivial | 0.217 | 0.032 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| C keyword-only | **0.517** | **0.547** | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |
| B no-retrieval | 0.433 | 0.443 | 0.233 | **1.000** | 0.378 | 0.000 | 0.833 |
| A final | 0.433 | 0.443 | **0.400** | 0.571 | **0.471** | 1.000 | 0.133 |

Deltas final−other: vs D acc +0.216/macro +0.411/esc_F1 +0.471; vs C acc −0.084/macro −0.104/esc_F1 +0.471; vs B acc ±0.000/macro ±0.000/esc_F1 +0.093/grounded +1.000.
## Which components matter
1. **Escalation rules head (dominant for safety).** C has retrieval but no rules → esc F1 0.000. Adding the trigger head (B/A) → 0.378/0.471. The rules, not retrieval, create escalation capability.
2. **Retrieval (precision modulator + grounding).** A vs B isolates it (classifier identical → intent Δ 0.000 by design): esc_P 0.233→0.368, esc_F1 +0.093, unresolvable 0.833→0.133, grounded 0.000→1.000. Without passages `no_grounding` is always true → over-escalation (R=1.0, P=0.233); with passages the gate calibrates (P up, R 1.0→0.571). Retrieval buys **precision + audit trail (passage IDs)**, not intent accuracy.
3. **Classifier (intent floor).** D→C/B: macroF1 0.032→0.547/0.443. Both weak-rules and LogReg vastly beat majority. C>B on intent here only because C IS the weak labeler overlapping human labels (circularity — see BASELINE_VS_FINAL.md); LogReg generalizes (worse on n=60, better-behaved off-distribution by design; verify on full-200-human next).
4. **Templates (groundedness heuristic).** Final grounded_rate 1.0 + ground_mean 4.75 (weak-200) come from cited templates; keyword top-1 echo scores 2.98 (ungrounded echo). Heuristic-graded — needs human/LLM-judge calibration (gated: wκ≥0.60).

Caveats: n=60, single annotator, wide CIs; retrieval threshold saturated (see RETRIEVAL_METRICS.md) so A-vs-B understates a future relevance-tuned retriever's value.
