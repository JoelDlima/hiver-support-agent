# 006 — Evaluation Decision (Hiver AppleSupport)

Date: 2026-09-10 | Owner: Swarm B | Status: FINAL v1
Base: `docs/research/evaluation/eval_strategy.md` + `docs/research/papers/academic_review.md` +
`docs/research/competitors/analysis.md` §§4–5

## Context
Prove trustworthy before any production claim. Four layers: A intent, B escalation,
C grounded reply, D retrieval (supporting). No single number suffices; every metric
reported as delta vs baselines, with a misleading-number disclosure in each report.

## Candidates
sklearn deterministic metrics (acc/macro-F1/per-intent/confusion; esc P/R/F1 + 2×2;
Recall@k/MRR/nDCG) | heuristic judge (offline) | LLM-as-judge (rubric, gated) |
RAGAS pair (faithfulness+correctness) | BLEU/ROUGE/BERTScore | golden human set
(200 + 60 overlap) | failure suite F1–F8 + red-team | baselines (random/majority,
no-retrieval LLM, BM25-only, prev version)

## Evidence (VERIFIED vs ESTIMATE)
- VERIFIED (academic track, 10 searches): Banking77 13k/77 — BERT ~93.6% full / ~85%
  10-shot, errors from label overlap; SetFit 8-shot ≈ full-tune (report mean±std/3 seeds,
  variance ±10pp); Twitter short-text → twitter-roberta + hashtag/emoji, 0.91–0.93 only on
  curated balanced sets; Loukas RAG few-shot ≈ 22× cheaper than GPT-4 path (copy
  MPNet-retriever + small-LLM + cost-per-1k column); Xu KG-RAG +77.6% MRR / −28.6% median
  resolution at LinkedIn; RAGAS faithfulness 0.95 pairwise (WikEval) BUT ARES/telecom/
  Deepchecks show relevance metrics misrank → gate on faithfulness+correctness pair +
  abstention, calibrate locally; GPT-4 judge ~80% ≈ human–human BUT position
  (Claude 23.8% swap-consistency) + verbosity (91.3% fail for non-GPT-4) biases → swap +
  reference-guided + CoT mitigations; Han 54-LLM study: r=0.95 with κ=0.45 (correlation
  lies), human κ̄=0.801, EM−κ deflation 33–41pp → 75-pair (50 grade + 25 attack/swap)
  blinded study, 2 humans + judge, report κ/α/EM/swap-consistency/verbosity-corr/z,
  Tier-1 = in-human-band + |z|<1 + swap ≥85%. Source: `papers/academic_review.md`.
- VERIFIED (eval strategy): acceptance bars v1 — intent acc ≥0.85 AND macro-F1 ≥0.80,
  no intent F1 <0.60; escalation recall ≥0.90, precision ≥0.70; groundedness mean ≥4.0,
  ≥80% ≥4; recall@3 ≥0.85; F1–F3/F6–F8 100% (F3 abstention ≥95%); F4/F5 ASR = 0 frozen;
  safety-FAIL recall ≥0.90; judge licensed only at groundedness weighted-κ ≥0.60.
- VERIFIED (competitor gap): no open AppleSupport-Twitter pipeline combines
  intent + grounded RAG + calibrated escalation + rigorous eval; closest bots report BLEU
  only (`ldulcic`, 79★) or 68% precision/no-rerank (`carlosrod723`); HF DistilBERT TWCS
  99.5% acc is keyword-pseudo-label inflation (cautionary tale); OOS recall collapse 58%
  (`aniqua14`) → must report OOS recall explicitly.
- ESTIMATE (external context, not our claim): Intercom Fin 76% resolution/~0.1%
  hallucination; mature triage 85–95% vs 40–50% rules ceiling (IrisAgent 2026).

## Decision
**Golden 200 (60 double-labeled overlap) + deterministic metrics + heuristic judge now +
LLM-judge GATED (licensed only at κ bars) + RAGAS faithfulness+correctness pair +
F1–F8 failure suite + 4 baselines. BLEU/ROUGE/BERTScore diagnostic-only (limits
disclosed: r≈0.22–0.32, punish paraphrase, ROUGE-recall rewards verbosity — use
ROUGE-L-F1; BERTScore can't detect hallucination). Thresholds tuned on DEV, frozen,
single test run; every report prints the §9 misleading-number disclosure.**

## Rejected — why
- Launch-on-containment/CSAT/BLEU: containment rewards stonewalling (~20% "contained"
  are drop-offs — Kaizo 2026); CSAT self-selection misses silent quitters; lexical
  metrics ≠ truth/safety. Banned as launch evidence.
- Recall@k alone: high recall coexists with wrong answers (misleading passage retrieved
  alongside gold — LLM-retEval 2024: Recall@5 ≈0.79 while answer failures rise with k;
  Facet-RAG: Evidence Override 42% vs Failure 6%). Report alongside, never instead of,
  answer scores.
- Ungated LLM-judge: inherits judge-model bias/version; static adversarial pass rates
  decay (12/12 in-band defenses broken >90% ASR adaptive — Narisetty 2026) → quarterly
  red-team with fresh payloads + attack budget disclosed.
- Accuracy-only: hides rare-intent collapse → always pair with macro-F1 + per-intent
  table + confusion matrix; escalation always 2×2 + false-negative human read.

## Cost / complexity / failure / scale
- Cost: deterministic + heuristic ≈ $0; golden labeling 2 annotators × ~2–3 days (one-off);
  LLM-judge only on 60-overlap + regression runs (Batch −50%).
- Complexity: `evaluation/` harness + `rubric.md` + frozen `golden_v1.csv`
  (id,text,intent_gold,escalate_gold,reason,gold_passage_ids,reference_reply,pii_flag,
  stratum); judge version pinned; annotators blind to model outputs.
- Failure: F1 empty → clarify (no escalate/hallucination); F2 huge → truncate within SLO;
  F3 no-retrieval → "don't know" + escalate (≥95%); F4/F5 injection → refuse + safe
  completion (ASR 0); F6 PII/secret → redact/block, never echo; F7 paraphrase consistency;
  F8 OOS/jailbreak → policy refusal + redirect. Fail-close on scanner outage.
- Scale: regression gate = no metric −2 pts without written justification; previous-version
  baseline every run; human audit sample each release.
