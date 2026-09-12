"""Promptfoo custom Python provider (keyless): AppleAgent(VirginRetriever(), brand="virgin").

Protocol (promptfoo python provider): ``call_api(prompt, options, context)``
returns ``{"output": str}`` or ``{"output": "", "error": str}``. Workers are
persistent, so the classifier + index load once per worker process.

Keyless by design: ``force_template: true`` (default) drops GROQ/OPENAI keys
from this worker's env so drafts always take the deterministic template path
— no network, no cost, byte-identical outputs. Set
``force_template: false`` in provider config to allow the live Groq path
(keyed runs should add llm-rubric asserts; none are in this config).

Output is a JSON string: intent, intent_confidence, decision,
escalate_reason, draft_reply, grounding_passage_ids, draft_path.
Keyless asserts in promptfooconfig.yaml parse it (contains/regex/javascript).

Source: promptfoo.dev/docs/providers/python (verified 2026-09-12).
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_AGENT = None


def _get_agent(force_template: bool):
    """Lazy singleton: VirginRetriever + AppleAgent(brand="virgin")."""
    global _AGENT
    if force_template:
        # Groq key lookup reads env per call; dropping here pins the worker
        # to the fail-closed template path even if the shell has keys set.
        for var in ("GROQ_API_KEY", "OPENAI_API_KEY"):
            os.environ.pop(var, None)
    if _AGENT is None:
        from scripts.run_virgin_eval import VirginRetriever
        from src.agent import AppleAgent

        try:
            retr = VirginRetriever()
        except Exception:
            retr = None  # agent fail-closes to empty passages -> escalate
        _AGENT = AppleAgent(retr, brand="virgin")
    return _AGENT


def call_api(prompt, options, context):
    """Promptfoo entry point. Returns {"output": json} (never raises)."""
    config = (options or {}).get("config", {}) or {}
    force_template = bool(config.get("force_template", True))
    try:
        agent = _get_agent(force_template=force_template)
        ctx_vars = ((context or {}).get("vars")) or {}
        text = ctx_vars.get("text", prompt)
        if not isinstance(text, str):
            text = str(text)
        res = agent.handle(text, brand="virgin")
        payload = {
            "intent": res.intent,
            "intent_confidence": round(float(res.intent_confidence), 3),
            "decision": res.decision,
            "escalate_reason": res.escalate_reason,
            "draft_reply": res.draft_reply,
            "grounding_passage_ids": list(res.grounding_passage_ids or []),
            "draft_path": (res.escalate_signals or {}).get("draft_path"),
        }
        return {"output": json.dumps(payload, ensure_ascii=False)}
    except Exception as e:  # provider failure -> promptfoo records error
        return {"output": "", "error": "virgin_provider: %s: %s" % (type(e).__name__, e)}
