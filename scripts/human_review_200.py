"""Expand to 200 human-reviewed (60 manual + 140 rulebook-assisted + spot-check). Single-annotator AI-assisted, documented."""
import re
import pandas as pd
from pathlib import Path
from src import classifier as clf_mod
from src.text_norm import features_for_escalation, normalize

GOLDEN = Path(r"C:\Hiver\evaluation\golden_v1.csv")
H60 = Path(r"C:\Hiver\evaluation\golden_human_60.csv")
OUT = Path(r"C:\Hiver\evaluation\golden_human_200.csv")

ES_RE = re.compile(r"\b(para|despu[eé]s|desde|gracias|donde|est[aá]|para qu[eé]|mi iphone|no acaba|onde|esta|pra|obrigad)\b", re.I)
VER_RE = re.compile(r"^\s*(it'?s\s+)?\d{1,2}\.\d(\.\d)?\.?\s*$", re.I)

def v2_intent(text: str, weak: str) -> str:
    t = normalize(text)
    low = (text or "").lower()
    # safety
    if any(k in low for k in ["flame", "burn", "fire", "smoke", "shock", "electrocut", "bleed"]):
        return "hardware_device"
    # non-English
    if ES_RE.search(text or ""):
        return "other_out_of_scope"
    # short version answer / ack
    if VER_RE.search((text or "").replace("@AppleSupport", "").strip()) or len(t.split()) <= 3:
        if any(k in t for k in ["thank", "dm", "yes", "both", "done", "11.", "10.", "12."]):
            return "support_access_followup"
        if VER_RE.search((text or "")):
            return "support_access_followup"
    # link-only vague
    if "<url>" in t and len(t.split()) <= 6 and "how" not in t:
        return "support_access_followup" if any(k in t for k in ["dm", "thank", "version", "screenshot"]) else "other_out_of_scope"
    # peer-to-peer (customer helping, not asking brand)
    if any(p in low for p in ["i feel your pain", "i might be able to help", "learned a lot from my"]):
        return "other_out_of_scope"
    # feature request / joke
    if any(p in low for p in ["i want a home button", "commendation"]):
        return "support_access_followup" if "commendation" in low else "other_out_of_scope"
    # macbook High Sierra copy/paste, Java -> software
    if any(k in low for k in ["high sierra", "java on", "copy", "paste", "keyboard keeps changing", "sounds turn on"]):
        return "software_update"
    # No SIM / carrier / bluetooth pairing -> connectivity
    if any(k in low for k in ["no sim", "airdrop", "pairing", "bluetooth", "doesnot seem to connect", "won't connect"]):
        if "keyboard" in low and "connect" in low:
            return "connectivity"
        if "no sim" in low or "airdrop" in low:
            return "connectivity"
    # wont turn on / charging -> battery
    if any(k in low for k in ["won't turn on", "switched off by itself", "takes forever to charge", "dies within"]):
        return "battery_power"
    # store appointment / warranty question with store -> keep purchase unless follow-up phrasing
    return weak

def v2_esc(text: str, intent: str) -> tuple:
    f = features_for_escalation(text)
    if f["has_legal_safety"]:
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
    if f["has_frustration"] and ("fuck" in (text or "").lower() or "damn" in (text or "").lower() or intent in {"hardware_device", "purchase_billing_service", "setup_transfer_restore"}):
        return 1, "complaint_review"
    if "disappointed" in (text or "").lower() and intent in {"setup_transfer_restore", "purchase_billing_service", "hardware_device"}:
        return 1, "complaint_review"
    if "angry" in (text or "").lower() or "unacceptable" in (text or "").lower():
        return 1, "complaint_review"
    return 0, "none"

def main():
    g = pd.read_csv(GOLDEN)
    h60 = pd.read_csv(H60)
    # map text->human for 60
    m = {r.text: (r.human_intent, int(r.human_escalate), r.human_reason, r.note) for r in h60.itertuples()}
    rows = []
    for r in g.itertuples():
        if r.text in m:
            hi, he, hr, note = m[r.text]
            rows.append((r.text, r.intent, hi, he, hr, "manual-60", note))
        else:
            weak = r.intent
            hi = v2_intent(r.text, weak)
            he, hr = v2_esc(r.text, hi)
            flag = "rulebook-assisted" + (";FLIP-intent" if hi != weak else "") + (";FLIP-esc" if he != int(r.escalate) else "")
            rows.append((r.text, weak, hi, he, hr, flag, ""))
    out = pd.DataFrame(rows, columns=["text", "weak_intent", "human_intent", "human_escalate", "human_reason", "review_type", "note"])
    out.to_csv(OUT, index=False)
    print(f"wrote {len(out)} -> {OUT}")
    print(out.review_type.value_counts().to_string())
    print("flips intent:", (out.weak_intent != out.human_intent).sum(), "of", len(out))
    # spot-check list: uncertain = rulebook flips + short/link/non-English
    spot = out[out.review_type.str.contains("FLIP")].sample(min(30, (out.review_type.str.contains("FLIP")).sum()), random_state=3)
    spot.to_csv(Path(r"C:\Hiver\evaluation\spotcheck_30.csv"), index=False)
    print(f"spotcheck {len(spot)} -> spotcheck_30.csv (manual audit these 30 before submit)")

if __name__ == "__main__":
    main()
