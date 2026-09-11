"""SSE smoke: POST /predict/stream, print event types + token count + final. No secrets."""
import httpx

events = []
tokens = []
final = {}
with httpx.stream("POST", "http://127.0.0.1:8104/predict/stream",
                  json={"text": "my train delayed, claim delay repay", "brand": "virgin"},
                  timeout=90) as r:
    for line in r.iter_lines():
        if not line or not line.startswith("data:"):
            continue
        payload = line[5:].strip()
        if payload == "[DONE]":
            events.append("DONE")
            continue
        import json as J
        try:
            ev = J.loads(payload)
        except Exception:
            continue
        events.append(ev.get("event", "?"))
        if ev.get("event") == "token" and ev.get("text"):
            tokens.append(ev["text"])
        if ev.get("event") == "final":
            final = ev
print("events:", events)
print("token_chars:", sum(len(t) for t in tokens))
print("final intent/decision/path:", final.get("intent"), final.get("decision"), (final.get("signals") or {}).get("draft_path"))
print("final draft:", (final.get("draft_reply") or "")[:160])
