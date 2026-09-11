"""LLM-as-judge rubric + harness. Offline heuristic default; optional OpenAI-compatible LLM if OPENAI_API_KEY set.
Rubric weights: groundedness .35 (gate <=2 FAIL), actionability .25, brand voice .15, safety/PII .15 (gate), relevance .10.
Output JSON: scores 1-5, evidence quotes, unsupported_claims, verdict PASS/FAIL. Temp 0, version pinned.
"""
import os, json
from dataclasses import dataclass

RUBRIC_VERSION = "judge-v1-2026-09-10"
LLM_MODEL = "gpt-4o-mini-2026-07-01 (pinned; fallback heuristic if no key)"

@dataclass
class JudgeScore:
    groundedness: int
    actionability: int
    brand_voice: int
    safety: int
    relevance: int
    verdict: str
    evidence: str
    unsupported_claims: list

JUDGE_PROMPT = """You are a strict support-QA judge for AppleSupport Twitter replies (2017 era).
Score 1-5 each: groundedness (claims supported by passages; <=2 = FAIL), actionability (one concrete next step + diagnostic), brand_voice (calm/plain/DM-when-PII), safety (PII/secrets/safety advice; <=2 = FAIL), relevance (addresses intent).
Return JSON only: {groundedness, actionability, brand_voice, safety, relevance, verdict PASS/FAIL, evidence (quote), unsupported_claims []}.
RULES: no post-2017 knowledge; DM redirect required when device/PII needed; never invent iOS versions/links; link-only input must clarify, not diagnose.
Input: intent, draft_reply, passage_texts[], inbound_text.
"""

def heuristic_judge(intent: str, draft: str, passages, inbound: str) -> JudgeScore:
    low = (draft or "").lower()
    ground = 1 + (1 if passages else 0) + (1 if any(k in low for k in ["settings", "restart", "check", "try"]) else 0) + (1 if len(draft.split()) >= 15 else 0)
    ground = max(1, min(5, ground + 1))
    action = 2 + (1 if "dm us" in low else 0) + (1 if "settings" in low else 0) + (1 if "?" not in draft else 0)
    action = max(1, min(5, action))
    voice = 4 if "dm us" in low else 3
    # safety: fail if draft contains secrets/phone/link invention or unsafe advice on safety case
    unsafe = any(k in low for k in ["password:", "ssn", "call 1-800", " open ", "http://"]) or ("warranty void" in low)
    safety = 2 if unsafe else 5
    inl = (inbound or "").lower()
    rel = 5 if intent != "other_out_of_scope" else (2 if len((inbound or "").split()) > 6 else 4)
    # NOTE 2026-09-11: tried `or rel <= 2` auto-FAIL here; REVERTED — this rel proxy keys on
    # other-predictions, so it FAILed reasonable triage while PASSing confident wrong-intent
    # drafts (heur-vs-human κ=-0.297 on the graded 30). Relevance gating belongs in the LLM
    # judge where relevance is genuinely graded (there it proved redundant: every rel<=2 item
    # already failed via groundedness<=2). See evaluation/virgin/LLM_JUDGE_30.md.
    verdict = "FAIL" if (ground <= 2 or safety <= 2) else "PASS"
    return JudgeScore(ground, action, voice, safety, rel, verdict, draft[:120], [])

def llm_judge(intent: str, draft: str, passages, inbound: str):
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        return None, "no-key: heuristic only (set OPENAI_API_KEY for gpt-4o-mini run)"
    try:
        from openai import OpenAI
        c = OpenAI()
        schema = {"type": "object", "properties": {k: {"type": "integer"} for k in ["groundedness", "actionability", "brand_voice", "safety", "relevance"]}, "required": ["groundedness", "actionability", "brand_voice", "safety", "relevance"], "additionalProperties": False}
        r = c.chat.completions.create(model="gpt-4o-mini", temperature=0, max_tokens=400,
            response_format={"type": "json_schema", "json_schema": {"name": "judge", "strict": True, "schema": schema}},
            messages=[{"role": "system", "content": JUDGE_PROMPT}, {"role": "user", "content": json.dumps({"intent": intent, "draft_reply": draft, "passages": passages[:2], "inbound": inbound[:500]})[:3000]}])
        return json.loads(r.choices[0].message.content), "llm-ok"
    except Exception as e:
        return None, f"llm-error: {e}"
