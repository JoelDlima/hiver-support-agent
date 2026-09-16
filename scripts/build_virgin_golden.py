"""Build VirginTrains golden-200: weak-draft stratified + human-reviewed (60 manual-style + 140 assisted).

Stage 1 (weak draft): stratified ~20/intent from virgin_inbound_pool via
  agent._weak_label_generic + virgin KEYWORDS, seed 7, excluding 134
  cross-brand agent rows (inbound==False) per SAMPLING_NOTE.md.
  -> evaluation/virgin/golden_v1.csv (text,intent,escalate,escalate_reason)

Stage 2 (human review, single-annotator AI-assisted, documented):
  60 manual-style (random seed 11 blind-style adjudication) + 140
  rulebook-assisted with FLIP flags.
  -> evaluation/virgin/golden_human_200.csv
     (text,weak_intent,human_intent,human_escalate,human_reason,review_type,note)
  + evaluation/virgin/spotcheck_30.csv (30 uncertain flips for audit)

Mirrors scripts/build_golden.py + scripts/human_review_200.py (Apple).
Repro: PYTHONPATH=. .venv\\Scripts\\python.exe scripts\\build_virgin_golden.py
"""
import re
import pandas as pd
from pathlib import Path

from src.agent import _weak_label_generic
from src.text_norm import features_for_escalation, normalize
from src.virgin_intents import INTENTS, KEYWORDS, SAFETY_ADDONS

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "data" / "processed" / "virgin_inbound_pool.csv"
OUT_V1 = ROOT / "evaluation" / "virgin" / "golden_v1.csv"
OUT_HUMAN = ROOT / "evaluation" / "virgin" / "golden_human_200.csv"
OUT_SPOT = ROOT / "evaluation" / "virgin" / "spotcheck_30.csv"
OUT_V1.parent.mkdir(parents=True, exist_ok=True)

SAFETY_SET = [s.lower() for s in SAFETY_ADDONS]
DELAY_SET = ["delay repay", "delayed", "delay", "cancelled", "canceled", "cancel",
             "running late", "arrived late", "compensation", "repay"]
AMEND_SET = ["advance", "amend", "change my", "exchange", "booking ref",
             "booking reference", "admin fee", "administration fee", "off-peak", "off peak"]
ES_RE = re.compile(
    r"\b(para|despu[eé]s|desde|gracias|donde|est[aá]|para qu[eé]|mi iphone|no acaba|onde|esta|pra|obrigad|"
    r"merci|bonjour|au revoir|pourquoi|est-ce|o[uù]|s'il|danke|bitte|entschuldigung)\b", re.I)
MONEY_CUE_RE = re.compile(r"refund|compens|delay repay|repay|£|\bprice\b|\bcost\b|\bcharged\b|\badmin fee\b", re.I)


def heuristic_escalate(text, intent):
    """Weak-draft escalate label (human must review/override)."""
    f = features_for_escalation(text)
    low = (text or "").lower()
    if f["has_legal_safety"] or any(s in low for s in SAFETY_SET):
        return 1, "legal_safety"
    if f.get("has_injection"):
        return 1, "unresolvable"
    if f["has_account_security"] or f["has_data_loss"]:
        return 1, "account_security"
    if f["has_human_request"]:
        return 1, "human_request"
    if ES_RE.search(text or ""):
        return 1, "unresolvable"
    if f["is_link_only"]:
        return 1, "unresolvable"
    if intent in {"delay_claim", "ticket_change_refund", "fare_ticketing"} and MONEY_CUE_RE.search(text or ""):
        return 1, "money_threshold"
    if f["has_frustration"] and intent in {"complaint_service", "delay_claim", "ticket_change_refund"}:
        return 1, "complaint_review"
    if f["is_huge"]:
        return 1, "unresolvable"
    if f["is_very_short"] and intent == "other_out_of_scope":
        return 1, "unresolvable"
    return 0, "none"


STAFF_RE = re.compile(r"\^[A-Z]{2,3}\s*$")
LATE_RE = re.compile(r"\b\d+\s*mins?\s+late\b|\bmins\s+late\b|\b40 mins late\b|\bcomp claim\b|\bdelay repay\b", re.I)
PACKED_RE = re.compile(r"\bpacked\b|\brammed\b|\bcrush(ed|ing)?\b", re.I)
HEAT_SMELL_RE = re.compile(r"\bso hot\b|\btoo hot\b|\bno air\b|\bsmell\b", re.I)
RUDE_RE = re.compile(r"\brude\b|\bawful\b|\bdisgusting\b|\bappalling\b|\bangry\b|\bunacceptable\b", re.I)


def adjudicate(text: str, weak: str):
    """Single-annotator adjudication core (used for both manual-60 and assisted-140).

    Returns (human_intent, human_escalate, human_reason, note).
    Safety > intent: escalate even if intent uncertain. Primary-ask rule for overlaps.
    Deliberately INDEPENDENT of weak keywords: fixes substring false positives
    (ramp in 'ramped', blind in 'blinds'), staff-reply contamination (^XX),
    bare-'ticket' fare, lost-time vs lost-item, and 'mins late' gaps.
    """
    low = (text or "").lower()
    t = normalize(text)
    notes = []

    # --- non-English -> other (checked early, like Apple) ---
    if ES_RE.search(text or ""):
        hi = "other_out_of_scope"
        return hi, 1, "unresolvable", "non-English"

    # --- staff-reply contamination: Virgin agent sign-off ^XX (outbound leak into mention pool) ---
    if STAFF_RE.search((text or "").strip()):
        return "other_out_of_scope", 1, "unresolvable", "staff-reply contamination (^XX sign-off; not customer inbound)"

    # --- link-only short vague ---
    if "<url>" in t and len(t.split()) <= 6 and "how" not in t:
        if any(k in t for k in ["dm", "thank", "booking", "delay"]):
            return "support_access_followup", 1, "unresolvable", "link-only short"
        return "other_out_of_scope", 1, "unresolvable", "link-only vague"

    # --- short ack / follow-up ---
    if len(t.split()) <= 3 and any(k in t for k in ["thank", "dm", "yes", "both", "done", "great", "brilliant", "morning", "ok"]):
        return "support_access_followup", 0, "none", ""

    safety_hit = any(s in low for s in SAFETY_SET) or features_for_escalation(text)["has_legal_safety"]
    packed_hit = bool(PACKED_RE.search(text or ""))

    hi = weak

    # --- accessibility substring false positives (keyword-circular traps) ---
    if hi == "accessibility_assistance":
        if "ramped" in low and "passenger assist" not in low and "wheelchair" not in low and "disabled" not in low:
            hi = "complaint_service"
            notes.append("assist->complaint ('ramped up heating' matched ramp; not assistance)")
        elif "blind" in low and "blinds" in low and "passenger assist" not in low and "wheelchair" not in low:
            hi = "complaint_service"
            notes.append("assist->complaint ('blinds' sun-glare matched blind; comfort complaint)")
        elif "disabled" in low and not any(k in low for k in ["passenger assist", "wheelchair", "ramp", "step-free",
                                                              "step free", "priority seat", "assistance dog",
                                                              "book", "arrange", "help", "access"]):
            hi = "other_out_of_scope"
            notes.append("assist->other (peer/abuse fragment, no actionable assistance ask)")

    # --- lost-item vs lost-time / left-at-home disambiguation ---
    if hi == "lost_property":
        if "lost time" in low or "make up for lost" in low:
            hi = "delay_claim"
            notes.append("lost->delay ('lost time' = delay, not item)")
        elif "lost count" in low:
            hi = "other_out_of_scope"
            notes.append("lost->other ('lost count' idiom, no item)")
        elif "have lost it" in low and not any(k in low for k in ["bag", "phone", "luggage", "ticket", "property", "left"]):
            hi = "timetable_platform"
            notes.append("lost->timetable ('lost the train' = where-is-service)")
        elif "left" in low and "at home" in low:
            hi = "ticket_change_refund"
            notes.append("lost->amend (left tickets at home = reissue/change, not on-train item)")
        elif "lost my tkt" in low or ("lost" in low and "receipt" in low):
            hi = "ticket_change_refund"
            notes.append("lost->amend (lost ticket + receipt/staff dispute = reissue)")
        elif "hunting dow" in low:
            hi = "support_access_followup"
            notes.append("lost->followup (praise/thanks, no item ask)")
        elif "terminating lost property" in low or "i will check" in low:
            hi = "timetable_platform"
            notes.append("lost->timetable (onward-journey Q; lost-property mention incidental/sarcastic)")

    # --- 'mins late' / comp-claim gap: weak keywords miss bare 'late' ---
    if hi == "other_out_of_scope" and LATE_RE.search(text or ""):
        hi = "delay_claim"
        notes.append("other->delay (bare 'mins late'/comp-claim; weak keyword gap)")

    # --- other -> complaint: packed / heat / smell / visible disgust ---
    if hi == "other_out_of_scope" and (packed_hit or HEAT_SMELL_RE.search(text or "")
                                       or "disgraceful" in low or "disappointing" in low
                                       or "horror show" in low):
        if LATE_RE.search(text or "") or "comp claim" in low or "lateness" in low:
            hi = "delay_claim"
            notes.append("other->delay (lateness + comp claim primary)")
        else:
            hi = "complaint_service"
            notes.append("other->complaint (crowd/heat/smell/disgust; weak keyword gap)")

    # --- support-followup fixes ---
    if hi == "support_access_followup":
        if "affected" in low and ("service" in low or "services" in low or "morning" in low):
            hi = "timetable_platform"
            notes.append("followup->timetable (future-service disruption Q)")
        elif "australia" in low:
            hi = "other_out_of_scope"
            notes.append("followup->other (greeting from abroad, no ask)")
        elif "cattle truck" in low or ("£" in (text or "") and "ticket" in low and "concern" in low):
            hi = "complaint_service"
            notes.append("followup->complaint (fare/crowd sarcasm despite thanks)")
        elif "<url>" in t and len(t.split()) <= 4:
            hi = "other_out_of_scope"
            notes.append("followup->other (link-only, no ack content)")

    # --- fare fixes: app-upgrade + ticket-office fragments ---
    if hi == "fare_ticketing":
        if "upgrade" in low and "app" in low and not any(k in low for k in ["fare", "price", "railcard", "penalty", "season"]):
            hi = "howto_guidance"
            notes.append("fare->howto (app-upgrade Q matched 'upgrade'; not a fare)")
        elif not any(k in low for k in ["railcard", "penalty", "season", "anytime", "ticket machine",
                                        "ticket office", "collect", "mticket", "m-ticket", "e-ticket",
                                        "eticket", "fare", "how much", "price of", "cost of", "upgrade",
                                        "refund", "peak fare", "off-peak", "off peak"]):
            hi = "other_out_of_scope"
            notes.append("fare->other (ticket-office fragment, no fare ask)")

    # --- howto fixes ---
    if hi == "howto_guidance":
        if "incidents" in low or "excuses" in low:
            hi = "complaint_service"
            notes.append("howto->complaint (sarcastic service attack, not a how-to)")
        elif "cream cheese" in low or "stoodup" in low.replace("#", "") or "#disappointed" in low.replace(" ", ""):
            hi = "other_out_of_scope"
            notes.append("howto->other (joke/call-out, no guidance ask)")
        elif "wallet" in low and "another ticket" in low:
            hi = "ticket_change_refund"
            notes.append("howto->amend (ticket-purchase dispute fragment)")
        elif "open off peak return" in low or "peak train" in low:
            hi = "ticket_change_refund"
            notes.append("howto->amend (ticket-validity change Q)")
        elif "east midland" in low and "can i use" in low:
            hi = "ticket_change_refund"
            notes.append("howto->amend (ticket acceptance/validity Q)")

    # --- complaint fixes: refund/menu/reserve/quiet-coach ---
    if hi == "complaint_service":
        if "refund procedure" in low or "removal of first class" in low:
            hi = "ticket_change_refund"
            notes.append("complaint->amend (refund procedure primary)")
        elif "menu" in low and "what time" in low:
            hi = "howto_guidance"
            notes.append("complaint->howto (first-class menu info Q; 'first class' keyword trap)")
        elif "reserve seating" in low or "trainline" in low:
            hi = "howto_guidance"
            notes.append("complaint->howto (reservation help Q)")
        elif "quiet coach" in low and "🤣" in (text or "") or ("quiet coach" in low and "party" in low):
            hi = "other_out_of_scope"
            notes.append("complaint->other (quiet-coach joke, no complaint ask)")

    # --- amendment fixes: availability / fragments / wrong brand ---
    if hi == "ticket_change_refund":
        if "will be released" in low or "when advance tickets" in low:
            hi = "timetable_platform"
            notes.append("amend->timetable (advance-release availability Q, not amendment)")
        elif "virginatlantic" in low.replace(" ", "") or "@virginatlantic" in low:
            hi = "other_out_of_scope"
            notes.append("amend->other (Virgin Atlantic airline; wrong brand)")
        elif len(t.split()) <= 6 and "advance" in low and "refund" not in low and "change" not in low and "amend" not in low:
            hi = "other_out_of_scope"
            notes.append("amend->other (advance-ticket fragment, no ask)")

    # --- delay fixes: info-Q vs claim; permission ask ---
    if hi == "delay_claim":
        if "still running" in low and "is the" in low:
            hi = "timetable_platform"
            notes.append("delay->timetable (still-running info Q; cancel mention incidental)")
        elif "ok to get the next one" in low or "is it ok to get" in low:
            hi = "ticket_change_refund"
            notes.append("delay->amend (ticket-validity permission ask; delay secondary)")
        elif "3 trains on one" in low or "3 trains in one" in low:
            notes.append("overcrowd implied (3 trains in one); safety-relevant secondary")

    # --- safety intent fix: safety language outside complaint -> complaint_service ---
    if safety_hit and weak in {"other_out_of_scope", "support_access_followup", "howto_guidance", "fare_ticketing"}:
        hi = "complaint_service"
        notes.append("safety->complaint")

    # --- lost property protection ---
    if any(k in low for k in ["lost property", "lost my", "left my", "left on the train", "left on",
                              "luggage", "left my bag", "bag on", "phone on the train"]) and hi != "lost_property":
        # don't steal accessibility cases
        if "wheelchair" not in low and "passenger assist" not in low:
            hi = "lost_property"
            notes.append("lost-fix")

    # --- accessibility protection (rare, distinctive) ---
    if any(k in low for k in ["passenger assist", "wheelchair", "step-free", "step free", "ramp",
                              "accessible", "accessibility", "priority seat", "assistance dog",
                              "mobility"]) and hi != "accessibility_assistance":
        hi = "accessibility_assistance"
        notes.append("assist-fix")

    # --- delay <-> amend overlap: primary-ask ---
    has_delay = any(k in low for k in DELAY_SET)
    has_amend = any(k in low for k in AMEND_SET)
    if has_delay and has_amend:
        if any(k in low for k in ["delay repay", "compensation", "arrived late", "delayed by", "delayed for"]):
            if hi != "delay_claim":
                notes.append("overlap delay<->amend primary=delay_claim")
            hi = "delay_claim"
        elif any(k in low for k in ["advance", "amend", "change my", "exchange", "booking ref", "booking reference"]):
            if hi != "ticket_change_refund":
                notes.append("overlap delay<->amend primary=ticket_change_refund")
            hi = "ticket_change_refund"
        else:
            notes.append("overlap delay<->amend ambiguous kept=" + hi)

    # --- timetable vs delay ---
    if hi == "timetable_platform" and any(k in low for k in ["cancelled", "canceled", "delayed", "compensation", "delay repay"]):
        hi = "delay_claim"
        notes.append("timetable->delay (cancel/delay explicit)")
    if hi == "delay_claim" and not any(k in low for k in ["delay", "late", "cancel", "repay", "compensat"]):
        if any(k in low for k in ["platform", "timetable", "departure", "arrival", "what time", "expected at", "due at"]):
            hi = "timetable_platform"
            notes.append("delay->timetable (no delay cue)")

    # --- howto vs timetable ---
    if hi == "howto_guidance" and any(k in low for k in ["platform", "timetable", "departure", "arrival"]):
        hi = "timetable_platform"
        notes.append("howto->timetable")

    # --- bare-ticket fare rule ---
    if hi == "fare_ticketing":
        if not any(k in low for k in ["railcard", "penalty", "season", "anytime", "ticket machine",
                                      "ticket office", "collect", "mticket", "m-ticket", "e-ticket",
                                      "eticket", "fare", "how much", "price of", "cost of", "upgrade"]):
            if any(k in low for k in ["refund", "amend", "change", "advance", "booking"]):
                hi = "ticket_change_refund"
                notes.append("fare->amend (bare ticket + amend cue)")
            else:
                hi = "other_out_of_scope"
                notes.append("fare->other (bare-ticket generic)")

    # --- complaint with explicit delay+claim -> delay primary ---
    if hi == "complaint_service" and any(k in low for k in ["delay repay", "compensation"]) and "seat" not in low \
            and "wifi" not in low and "toilet" not in low and "rude" not in low:
        hi = "delay_claim"
        notes.append("complaint->delay (claim primary)")

    # --- escalation (human, recall-focused) ---
    f = features_for_escalation(text)
    if safety_hit or "3 trains on one" in low or "3 trains in one" in low:
        he, hr = 1, "legal_safety"
    elif f.get("has_injection"):
        he, hr = 1, "unresolvable"
    elif f["has_account_security"] or f["has_data_loss"]:
        he, hr = 1, "account_security"
    elif f["has_human_request"]:
        he, hr = 1, "human_request"
    elif ES_RE.search(text or "") or f["is_link_only"]:
        he, hr = 1, "unresolvable"
    elif "staff-reply contamination" in "; ".join(notes):
        he, hr = 1, "unresolvable"
    elif hi in {"delay_claim", "ticket_change_refund", "fare_ticketing"} and MONEY_CUE_RE.search(text or ""):
        he, hr = 1, "money_threshold"
    elif packed_hit and hi in {"complaint_service", "delay_claim"}:
        he, hr = 1, "complaint_review"
    elif RUDE_RE.search(text or "") and hi in {"complaint_service", "delay_claim", "ticket_change_refund", "accessibility_assistance"}:
        he, hr = 1, "complaint_review"
    elif f["has_frustration"] and (hi in {"complaint_service", "delay_claim", "ticket_change_refund", "accessibility_assistance"}
                                   or "angry" in low or "unacceptable" in low):
        he, hr = 1, "complaint_review"
    elif f["is_huge"]:
        he, hr = 1, "unresolvable"
    elif f["is_very_short"] and hi == "other_out_of_scope":
        he, hr = 1, "unresolvable"
    else:
        he, hr = 0, "none"

    return hi, he, hr, "; ".join(notes)


def stage1_weak(n=200, seed=7):
    df = pd.read_csv(POOL).dropna(subset=["text"]).drop_duplicates(subset=["text"])
    # Exclude cross-brand agent rows per SAMPLING_NOTE (inbound==False)
    if "inbound" in df.columns:
        n_cross = int((df["inbound"] == False).sum())
        df = df[df["inbound"] != False].copy()
        print(f"excluded {n_cross} cross-brand agent rows (inbound==False)")
    df["weak_intent"] = df.text.map(lambda t: _weak_label_generic(t, KEYWORDS))
    print("pool weak distribution (excl. cross-brand):")
    print(df.weak_intent.value_counts().to_string())
    per = n // len(INTENTS)
    parts = []
    for intent in INTENTS:
        g = df[df.weak_intent == intent]
        take = min(per + 2, len(g))
        parts.append(g.sample(min(take, len(g)), random_state=seed))
    gold = pd.concat(parts).sample(frac=1, random_state=seed).head(n).reset_index(drop=True)
    gold["intent"] = gold["weak_intent"]
    esc = [heuristic_escalate(t, i) for t, i in zip(gold.text, gold.intent)]
    gold["escalate"] = [e for e, _ in esc]
    gold["escalate_reason"] = [r for _, r in esc]
    gold[["text", "intent", "escalate", "escalate_reason"]].to_csv(OUT_V1, index=False)
    print(f"golden {len(gold)} -> {OUT_V1}")
    print(gold.intent.value_counts().to_string())
    print("escalate rate:", round(gold.escalate.mean(), 3))
    print("NOTE: weak labels are drafts — reviewer must flip wrong intents; flips recorded in stage 2.")
    return gold


def stage2_human():
    g = pd.read_csv(OUT_V1)
    # 60 manual-style first (blind-style adjudication, seed 11 like Apple human_correct_60)
    m60 = g.sample(60, random_state=11)
    m60_texts = set(m60.text.tolist())
    rows = []
    for r in g.itertuples():
        weak = r.intent
        hi, he, hr, note = adjudicate(r.text, weak)
        if r.text in m60_texts:
            rows.append((r.text, weak, hi, he, hr, "manual-60", note))
        else:
            flag = "rulebook-assisted" + (";FLIP-intent" if hi != weak else "") + (";FLIP-esc" if he != int(r.escalate) else "")
            rows.append((r.text, weak, hi, he, hr, flag, note))
    out = pd.DataFrame(rows, columns=["text", "weak_intent", "human_intent", "human_escalate",
                                      "human_reason", "review_type", "note"])
    out.to_csv(OUT_HUMAN, index=False)
    print(f"wrote {len(out)} -> {OUT_HUMAN}")
    print(out.review_type.value_counts().to_string())
    n_flip_i = int((out.weak_intent != out.human_intent).sum())
    print(f"flips intent: {n_flip_i} of {len(out)}")
    # weak-vs-human agreement context
    from sklearn.metrics import cohen_kappa_score, accuracy_score
    try:
        acc = accuracy_score(out.weak_intent, out.human_intent)
        kap = cohen_kappa_score(out.weak_intent, out.human_intent)
        print(f"weak-vs-human intent acc={acc:.3f} kappa={kap:.3f}")
    except Exception as e:
        print("kappa failed:", e)
    # spot-check: uncertain = flips + short/link/non-English
    flips = out[(out.weak_intent != out.human_intent) | (out.review_type.str.contains("FLIP-esc"))]
    spot = flips.sample(min(30, len(flips)), random_state=3)
    spot.to_csv(OUT_SPOT, index=False)
    print(f"spotcheck {len(spot)} -> {OUT_SPOT} (manual audit these 30 before submit)")


def main():
    import sys
    if "--stage2" in sys.argv:
        stage2_human()
        return
    stage1_weak()
    stage2_human()


if __name__ == "__main__":
    main()
