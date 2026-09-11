# REPRO_CHECK — Swarm A (§32) — 2026-09-10; re-verified 2026-09-11 (Virgin headline sync)

Venv `C:\Hiver\.venv` (Python 3.12.10), `PYTHONPATH=C:\Hiver`. No installs outside `C:\Hiver`.

## 2026-09-11 re-verification (PDF-strict run)
| Command | Result |
|---|---|
| `pytest C:\Hiver\tests -q` | PASS — 17 passed in ~2–6s |
| `scripts/run_virgin_eval.py` | PASS — weak final 0.795/0.793 esc 0.641; human-200 headline final 0.660/0.672 esc 0.580/0.784/0.667; weak-vs-human 0.795 κ 0.772 |
| `scripts/run_virgin_judge.py` | PASS — safety 1.000 (n=3), money 0.800 (16/20), esc acc 0.855 κ 0.577, ground mean 4.28 |
| eval+judge+tests timed | 20.4s total — well under 15-min PDF limit |
| TestClient `/healthz` `/readyz` `/predict` virgin+apple | PASS — virgin delay→delay_claim/escalate/money_review; apple battery→battery_power/auto_handle |
| Exact-text failure re-probe F1–F7 | 7 PASS / 2 PARTIAL / 0 FAIL (F4a/F5/F6 fixed since 09-10; F4a intent + F7 direction + F2 bare-still-running fragility remain) |

| Command | Result |
|---|---|
| `C:\Hiver\.venv\Scripts\python.exe -m pytest C:\Hiver\tests -q` | PASS — 10 passed in ~3s (4 `test_agent` + 6 `test_reliability`) |
| `C:\Hiver\.venv\Scripts\python.exe C:\Hiver\scripts\smoke_fail.py` | PASS — 8/8 fail-closed, p50 230.6ms p95 260.4ms |
| TestClient `POST /predict` (battery/empty/5000-char) + `GET /metrics` | PASS — 200s, `truncated:true` on huge, metrics counts+avg OK |
| `py_compile` `frontend/app.py`, `backend/main.py`, `tests/test_reliability.py` | PASS |
| Streamlit server launch | NOT RUN (headless) — `app.py` verified by compile + direct `AppleAgent(Retriever()).handle` probe (battery→auto, 277ms, 2 passage IDs) |

Note: full README pipeline (`build_kb` → `run_eval`) not re-run (artifacts present, CPU ~15min);
code-level repro above covers Swarm A scope. `frontend/app.py` run: `streamlit run frontend/app.py` from `C:\Hiver`.
