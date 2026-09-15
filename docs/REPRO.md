# Reproduction — headline results in under 15 minutes

Rule (PS): "README must let us reproduce your headline results in under 15 minutes."
Everything below is CPU-only, Windows PowerShell, all paths inside the repo
(no absolute machine paths — roots resolve from `__file__`). No API key is
needed for any headline number: the LLM drafter is fail-closed to templates
when `GROQ_API_KEY` is unset, so keyless output is deterministic.

Headline being reproduced (human-200, `evaluation/virgin/results_human200.csv`):
final **0.795 acc / 0.803 macroF1**, esc **0.778 / 0.757 / 0.767**, ground mean **4.21**.

## Fast path (~1 minute; artifacts are committed)

Models and indexes are committed, so the two headline-producing commands run
directly against frozen artifacts:

```powershell
# 0. venv + deps (once; ~3-5 min the very first time, then cached)
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 1. re-run the headline eval (read-only over goldens; ~40s)
$env:PYTHONPATH="<repo-root>"
python scripts\run_virgin_eval.py
#   -> evaluation/virgin/results_human200.csv  (final row: 0.795 / 0.803, esc F1 0.767)
#   -> evaluation/virgin/BASELINE_VS_FINAL.md  (trivial / simple / final tables)

# 2. judge agreement + safety/money recall (~10s)
python scripts\run_virgin_judge.py
#   -> evaluation/virgin/JUDGE_AGREEMENT.md inputs (esc acc 0.915, k 0.715)

# 3. full test suite incl. 9/9 failure-probe regressions (~2-3 min)
python -m pytest tests -q
```

Historic verification: `docs/REPRO_CHECK.md` (eval+judge+tests timed at 20.4s
on the frozen artifact path; full suite 75 passed as of V2).

## Full rebuild path (~6-8 minutes; only if you want to regenerate artifacts)

```powershell
# raw data: data/raw/twcs.csv (gitignored; download once via kagglehub,
# dataset thoughtvector/customer-support-on-twitter -- see README Prerequisites)
python scripts\build_virgin_kb.py      # -> virgin_kb.csv (27,172) + inbound pool (37,444)
python scripts\build_virgin_index.py   # -> TF-IDF NN index (build ~0.5s, p50 7.9ms)
python scripts\train_virgin.py         # -> models/intent_virgin.pkl (30k weak, balanced)
python scripts\run_virgin_eval.py      # -> headline tables (bit-identical to committed CSVs)
```

Total from a clean clone with the dataset present: ~6-8 min CPU (well under
the 15-minute budget; measure on the reviewer machine, do not quote without
re-timing).

## Live demo (optional, not part of the 15-min claim)

```powershell
uvicorn backend.main:app --host 127.0.0.1 --port 8000   # backend
cd frontend-next; npm install; $env:FASTAPI_URL="http://127.0.0.1:8000"; npm run dev  # :3000
```

## Honesty notes

- The headline numbers are produced from the **frozen** classifier
  (`models/intent_virgin.pkl`) + committed index; the rebuild path reproduces
  them from weak labels (same seed 42 recipe) — train-subset acc 0.969 is
  optimistic/circular and is disclosed as such in `BASELINE_VS_FINAL.md` §A.
- Golden sampling + labeling method: `evaluation/virgin/SAMPLING_NOTE.md`
  (stratified n=200, seed 7) + `docs/ANNOTATION_PROTOCOL.md`.
- Re-run outputs are deterministic keyless; with a key set the judge/eval
  numbers are unchanged because eval drafts are template-path.
