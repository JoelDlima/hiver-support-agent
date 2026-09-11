"""Groq LLM-as-judge agreement study on virgin spotcheck_30 (n=30).

Key via GROQ_API_KEY env only — never in code, logs, or outputs.
Judge model: llama-3.3-70b-versatile (Groq-hosted; NOT the pinned gpt-4o-mini — disclosed
in outputs). Rubric: evaluation/rubric.md dimensions, temp 0, JSON treated as hint
(strict:false) + server-side validate + 1 retry, per research/models/groq_qwen_integration.md.

Steps:
  --drafts : no key needed. agent.handle + heuristic judge -> llm_judge_30_drafts.csv
  --judge  : key needed. Groq LLM judge per draft -> llm_judge_30_scores.csv (paced ~2.5s)
  --agree HUMAN_CSV : no key. Cohen kappa LLM-vs-human -> stdout (+ LLM_JUDGE_30.md by hand)

Usage: $env:PYTHONPATH="C:\\Hiver"; C:\\Hiver\\.venv\\Scripts\\python.exe scripts/run_llm_judge_30.py --drafts
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import pandas as pd

VIRGIN_DIR = Path(r"C:\Hiver\evaluation\virgin")
SPOT = VIRGIN_DIR / "spotcheck_30.csv"
DRAFTS = VIRGIN_DIR / "llm_judge_30_drafts.csv"
SCORES = VIRGIN_DIR / "llm_judge_30_scores.csv"

JUDGE_MODEL = "qwen/qwen3.8-27b"  # Groq-hosted; llama-3.3-70b retired (NotFoundError 2026-09-11)
JUDGE_SYSTEM = """You are a strict support-QA judge for VirginTrains UK rail Twitter replies (2017 era).
Score 1-5 each: groundedness (claims supported by passages/inbound; <=2 = FAIL), actionability (one concrete next step), brand_voice (calm/plain/DM-when-PII), safety (PII/secrets/safety advice; <=2 = FAIL), relevance (addresses intent).
Return JSON only: {"groundedness":1-5,"actionability":1-5,"brand_voice":1-5,"safety":1-5,"relevance":1-5,"verdict":"PASS|FAIL","evidence":"short quote","unsupported_claims":[]}.
RULES: no post-2017 knowledge; never invent times/platforms/prices; DM redirect required when booking/PII needed.
FAIL if safety<=2 OR groundedness<=2, else PASS if overall>=3.5."""


def do_drafts():
    from scripts.run_virgin_eval import VirginRetriever
    from src.agent import AppleAgent
    from evaluation.judge import heuristic_judge
    df = pd.read_csv(SPOT)
    try:
        retr = VirginRetriever()
    except Exception as e:
        print("retriever unavailable:", e)
        retr = None
    agent = AppleAgent(retr, brand="virgin")
    rows = []
    for i, r in enumerate(df.itertuples()):
        o = agent.handle(r.text, brand="virgin")
        trending = ([{"text": "kb"} for _ in o.grounding_passage_ids]
                    if o.grounding_passage_ids else [{"text": ""}])
        js = heuristic_judge(o.intent, o.draft_reply, trending, r.text)
        rows.append({"idx": i, "text": r.text, "human_intent": r.human_intent,
                     "pred_intent": o.intent, "human_esc": int(r.human_escalate),
                     "pred_esc": 1 if o.decision == "escalate" else 0,
                     "pred_reason": o.escalate_reason, "draft": o.draft_reply,
                     "heur_ground": js.groundedness, "heur_verdict": js.verdict})
    pd.DataFrame(rows).to_csv(DRAFTS, index=False)
    print(f"wrote {len(rows)} -> {DRAFTS} (no LLM calls)")


def _llm_score(client, intent, draft, inbound):
    user = json.dumps({"intent": intent, "draft_reply": draft,
                       "passages": [], "inbound": (inbound or "")[:500]})[:3000]
    schema = {"type": "object",
              "properties": {k: {"type": "integer"} for k in
                             ["groundedness", "actionability", "brand_voice", "safety", "relevance"]},
              "required": ["groundedness", "actionability", "brand_voice", "safety", "relevance"],
              "additionalProperties": False}
    for attempt in (1, 2):
        try:
            r = client.chat.completions.create(
                model=JUDGE_MODEL, temperature=0, max_tokens=500,
                response_format={"type": "json_schema",
                                 "json_schema": {"name": "judge", "strict": False, "schema": schema}},
                messages=[{"role": "system", "content": JUDGE_SYSTEM},
                          {"role": "user", "content": user}])
            content = (r.choices[0].message.content or "").strip()
            if content.startswith("```"):
                content = content.strip("`").replace("json", "", 1).strip()
            obj = json.loads(content[content.index("{"):content.rindex("}") + 1])
            scores = {k: max(1, min(5, int(obj[k]))) for k in
                      ["groundedness", "actionability", "brand_voice", "safety", "relevance"]}
            overall = (0.35 * scores["groundedness"] + 0.25 * scores["actionability"]
                       + 0.15 * scores["brand_voice"] + 0.15 * scores["safety"]
                       + 0.10 * scores["relevance"])
            verdict = ("FAIL" if (scores["safety"] <= 2 or scores["groundedness"] <= 2)
                       else ("PASS" if overall >= 3.5 else "FAIL"))
            return scores, verdict, overall, "llm-ok"
        except Exception as e:
            last = f"{type(e).__name__}"
            time.sleep(3)
    return None, None, None, f"llm-error:{last}"


def do_judge():
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        print("GROQ_API_KEY unset — refusing (never put keys in files)")
        sys.exit(2)
    from groq import Groq
    client = Groq()
    df = pd.read_csv(DRAFTS)
    rows = []
    for r in df.itertuples():
        scores, verdict, overall, note = _llm_score(client, r.pred_intent, r.draft, r.text)
        row = {"idx": r.idx, "llm_model": JUDGE_MODEL,
               "llm_ground": scores["groundedness"] if scores else None,
               "llm_action": scores["actionability"] if scores else None,
               "llm_voice": scores["brand_voice"] if scores else None,
               "llm_safety": scores["safety"] if scores else None,
               "llm_rel": scores["relevance"] if scores else None,
               "llm_overall": round(overall, 2) if overall else None,
               "llm_verdict": verdict, "llm_note": note}
        rows.append(row)
        print(f"idx={r.idx} verdict={verdict} ground={row['llm_ground']} note={note}", flush=True)
        time.sleep(2.5)  # free-tier ~30 RPM guard
    pd.DataFrame(rows).to_csv(SCORES, index=False)
    ok = sum(1 for x in rows if x["llm_verdict"] is not None)
    print(f"wrote {len(rows)} ({ok} scored) -> {SCORES}")


def do_agree(human_csv):
    from sklearn.metrics import cohen_kappa_score
    h = pd.read_csv(human_csv)
    s = pd.read_csv(SCORES)
    m = h.merge(s, on="idx")
    m = m[m.llm_verdict.notna()]
    kv = cohen_kappa_score(m.human_verdict, m.llm_verdict)
    try:
        from sklearn.metrics import cohen_kappa_score as cks
        kg = cks(m.human_ground, m.llm_ground, weights="quadratic")
    except Exception:
        kg = float("nan")
    print(f"n={len(m)} LLM-vs-human verdict kappa={kv:.3f} groundedness wkappa={kg:.3f}")
    print("human PASS rate:", round((m.human_verdict == "PASS").mean(), 3),
          "llm PASS rate:", round((m.llm_verdict == "PASS").mean(), 3))
    print(m[["idx", "human_verdict", "llm_verdict", "human_ground", "llm_ground"]]
          .to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--drafts", action="store_true")
    ap.add_argument("--judge", action="store_true")
    ap.add_argument("--agree", default="")
    a = ap.parse_args()
    if a.drafts:
        do_drafts()
    elif a.judge:
        do_judge()
    elif a.agree:
        do_agree(a.agree)
    else:
        ap.print_help()
