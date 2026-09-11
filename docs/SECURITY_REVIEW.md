# SECURITY_REVIEW — Swarm A (§30) — 2026-09-10

Scope: `src/`, `backend/`, `scripts/`, `configs/` inside `C:\Hiver`. Method: pattern grep + `scripts/smoke_fail.py` + API probes.

## 1. Secrets — no hardcode, env vars
- Grep `api_key|AKIA|ghp_|sk-|BEGIN.*PRIVATE` in `src/`, `backend/`, `configs/`: **0 matches**.
- Grep `api_key|...|secret|password` in `scripts/`: 2 benign hits only —
  `scripts/smoke_fail.py:5` injection-test string ("reveal password", intentional adversary case),
  `scripts/build_retrieval_baseline.py:57` probe ("forgot apple id password reset", domain keyword).
- Grep `password` in `src/`: only domain logic — `intents.py` Apple-ID keyword/template
  ("Don't share passwords here — DM us"), `text_norm.py` `has_injection` pattern
  ("reveal password") and `has_account_security` ("password reset not working"). No credential values.
- `os.environ/getenv/.env` in `src/backend/scripts`: **0 matches** — no secret loading needed;
  nothing to put in env vars today. If LLM keys are added later: env var + `st.secrets`/vault,
  never commit `.env`, add gitleaks pre-commit + CI gate (see research log 2026-09-10).
- Data files contain literal user "password" words (Twitter corpus) — expected, not leaked app secrets.
- Finding: **PASS — no hardcoded secrets. Residual: add `.gitleaks.toml` + CI scan when keys arrive.**

## 2. Input handling
- Length cap 2000: `backend/main.py` truncates `raw[:2000]`, sets `truncated:true` in
  response + JSON log; `frontend/app.py` `max_chars=2000`. `agent.handle` already escalates
  `is_huge (>500)` → `unresolvable`, so 5000-char input escalates (verified).
- PII DM-redirect: account templates never ask for passwords publicly
  (`intents.py:48` "Don't share passwords here — DM us"); empty/unknown drafts ask for
  "device + iOS version" via DM only. No PII echoed in logs (log line = request_id/intent/
  decision/latency only, no text).
- Injection → escalate: `text_norm.has_injection` (ignore previous/reveal password|system/
  system prompt/jailbreak/dan mode/do anything now) → `agent.decide_escalation` → `escalate/
  unresolvable`. Verified below. OWASP LLM01 posture: deterministic escalate + least-privilege
  (no tools/credentials in model path) + logging; no LLM free-call to hijack (template drafts).

## 3. Tests run + findings
- `pytest C:\Hiver\tests -q`: **10 passed** (4 existing + 6 new `test_reliability.py`).
- `scripts/smoke_fail.py` (2026-09-10): all 8 cases correct —
  `''/'   '`→escalate/unresolvable; `x*2000`→escalate/unresolvable;
  `ignore prev…reveal password`→escalate/unresolvable; `flame/burned`→escalate/legal_safety;
  `thank you!!`→auto/none; `https://t.co/abc`→escalate/unresolvable;
  `I want a human`→escalate/human_request. Latency p50 230.6ms / p95 260.4ms.
- API probes (TestClient): `/predict` battery→200 auto; empty→200 escalate;
  5000-char→200 escalate + `truncated:true`; `/metrics`→200 with counts/avg. `/predict` unbroken.
- Finding: **PASS — injection, safety, empty/huge, link-only, human-request all fail-closed
  to escalate. No secret leakage in code, logs, or drafts.**
