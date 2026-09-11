# Hiver frontend-next (Next.js 14 + three.js, BFF to FastAPI)

Modern demo: brand switch (VirginTrains/AppleSupport), live pipeline timeline with measured
stage ms (classify/retrieve/draft from `/predict`), SSE streaming Groq draft tokens,
3D retrieval graph (query=center, passages=satellites sized by live score) + ranked list,
confidence bars with threshold captions, live heuristic judge, live `/metrics` (5s poll).

## Run (2 terminals, all inside C:\Hiver)

```powershell
# 1. backend (holds GROQ key server-side; key NEVER in this folder)
$env:PYTHONPATH="C:\Hiver"
$env:GROQ_API_KEY="gsk_..."   # session only; unset = template path (fail-closed)
& "C:\Hiver\.venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --workers 1

# 2. frontend
cd C:\Hiver\frontend-next
npm install
$env:FASTAPI_URL="http://127.0.0.1:8000"
npm run dev    # http://localhost:3000  (or: npm run build; npm run start)
```

## Why judges believe it
Every technical shown is measured live: stage ms from the real agent call, passage IDs +
scores from the real KB index, draft tokens streamed from Groq (or template with
`draft_path`+reason shown), escalation + reason from the real policy, metrics from the
real counters. No mocked numbers anywhere — `draft_path: template|groq` and
`groq_reason: no-key|validation-fail|error|ok` are always visible.
Key rule: browser → `/api/*` → FastAPI. `GROQ_API_KEY` never has a `NEXT_PUBLIC_` prefix
and never appears in this folder (see `.gitignore`: `.env` blocked, `.env.example` only).
