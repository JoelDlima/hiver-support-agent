# Post-critic fetch log — hiver-support-agent-audit-6d951f (Step 13)

## Gap triage (from critic-findings-*.json)

Reviewed all 28 findings (7 dialectic + 7 depth + 7 width + 7 instruction). Vault-search verified that
every finding except one is patcher-addressable from in-vault evidence (2+ notes each): security cluster
(4 notes), sklearn split primitives (2 notes), selective-prediction toolkit (1 note + 6 methodology notes),
RAGAS traceability (repo + FaithJudge + MLM mechanism), IntentBERT/OOD (3 notes), DSPy/LangChain (4 notes),
brand EDA (2 notes), agreement machinery (5 notes).

## Sole fetch-worthy gap: W1 (LangSmith primary docs)

- Searched: LangSmith evaluate/pytest/evaluation-types official docs.
- docs.smith.langchain.com host is DEAD (DNS failure on both URLs) — canonical docs moved to docs.langchain.com/langsmith/*.
- Fetched 1: how-to-evaluate-agents-docs-by-langchain (3145 words) — evaluate()/aevaluate() SDK, datasets, code+UI evaluators, openevals prebuilt evaluators, experiment metadata, max_concurrency, experiments table.
- Patcher guidance: cite the new note for hosted-parity (W1/D3); acknowledge the dead host as a docs-freshness data point (verify-as-of-2026-09-14 rule in action).

## Unfilled (acknowledge, don't fabricate)

- TMobileHelp-vs-AmazonHelp pilot gate (D4): requires local EDA on raw twcs.csv, not fetchable. Patcher must frame as a required pilot measurement, not a fetched fact.
- Per-label CI-width demonstration at n=150 (cc-6/I-gates): design arithmetic, not literature. Patcher keeps it as NOT MEASURED with the acceptance rule stated.
