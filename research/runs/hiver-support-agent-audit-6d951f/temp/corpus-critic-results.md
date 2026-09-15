# Corpus-critic results — hiver-support-agent-audit-6d951f (Step 8)

6 gaps (cc-1..cc-6), 3 gap-fill fetchers, ~18 new notes. Corpus now 118 notes, 0 retracted.

## Per-gap outcome

- **cc-1 brand-selection EDA — STRENGTHENED.** New: exact-corpus EDA with per-brand tables (AmazonHelp 169,840 tweets; AppleSupport 106,860; median response TMobileHelp 2.75min vs AppleSupport 70.97min) + 1.5M-tweet 7-intent classifier precedent (inbound ~55%, 7-category routing). Apple default now testable against airline/telecom alternatives on reply-rate × thread-quality × temporal-spread. No overturn (no source crowns a brand), but the decision is now measurable.
- **cc-2 noisy-tweet classifier transfer — STRENGTHENED BUT CONDITIONALIZED.** New: Shelmanov ACL-2022 (full-layer MC-dropout beats MaxProb on text-class rejection curves; cheap last-layer variant ≈ free) qualifies Xin/Varshney; Dutch-tweet benchmark favors Twitter-pretrained backbones over SetFit-once-run; softmax-revisited study keeps single-pass softmax cost-effective. Net: MC-routing viable in-domain with full-layer dropout; Twitter backbone required; MaxProb stays the cost default.
- **cc-3 learned-sparse/store ops — STRENGTHENED WITH CAVEAT.** New: hybrid +8-15% concentrated on exact-term queries; pgvector + tsvector + RRF-in-one-SQL concrete recipe; SPLADE priced (query-expansion latency ~6× unless doc-only). Two-index + rerank default stands; doc-only SPLADE logged as simplification path.
- **cc-4 judge demotions + harness parity — JUDGE CORE STRENGTHENED, HARNESS CHOICE CHALLENGED.** New: FaithJudge EMNLP-2025 (RAGAS-zero-shot <78% bal-acc, HHEM-2.1 competitive but far from parity → demotion stands); pointwise-vs-pairwise study (pairwise flips ~35% vs ~9% absolute → pointwise choice supported); Langfuse official CI/CD datasets/experiment docs → hosted-parity is real, code-first default needs explicit justification, not comparison blogs.
- **cc-5 calibration machinery — STRENGTHENED.** New: Traub NeurIPS-2024 (AUGRC supersedes AURC; rankings change on 5/6 datasets → report AUGRC, keep AURC for comparability); UniCR-2025 (learned calibration head + conformal risk control beats thresholds under shift → strongest calibrator citation); ACI-2021 (streaming coverage recipe + weight-collapse caution). Toolkit arithmetic now independently verifiable via fd-shifts/TorchUncertainty implementations.
- **cc-6 annotation gates — STRENGTHENED WITH QUALIFICATION.** New: Zapf-2016 (N=200 ≈ nominal bootstrap coverage, N=100 not → n=200 stands); Hughes-2022 (bootstrap under-dispersed at small n/high α → use analytical jackknife CI, not KALPHA default → CI method changes, gate number holds); Krippendorff benchmarks sourced (≥0.80/0.667); iSarcasm (author-labeled Twitter κ≈0.37 → sarcasm carve-out empirically forced). Dangerous overturn (rankings stable in 0.667-0.80) did NOT materialize.

## Confidence updates to committed positions

- Leakage-split: unchanged (high) — now with brand-comparison numbers to act on.
- SetFit-routing: 0.72 → conditional hold — add full-layer-dropout requirement + Twitter-backbone requirement + MaxProb-cost-default framing.
- Hybrid-retrieval: 7.5/10 → hold — exact-term lift quantified (+8-15%), pgvector-SQL recipe in hand.
- Caged-judge: high (architecture) → hold; harness build-vs-buy downgraded to contested — draft must justify code-first vs Langfuse/LangSmith parity explicitly.
- Escalation: 7/10 → hold — AUGRC replaces AURC as primary, ACI noted as streaming extension.
- Golden-gate: 0.75 → hold — CI method switches to jackknife at n=200.

No overturning source found for any committed position after adversarial search: all six positions gain confidence (adversarial search with no substantive challenges).
