"""Apply human review corrections to 60-sample (reviewer: AI acting as annotator, 2026-09-10).
Weak labels from keywords are drafts; this file records flips with reasons.
Sampling: random 60 from golden_v1, seed 11. Double-label note: single annotator + spot-check; kappa vs weak = agreement proxy."""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "evaluation" / "human_review_60_draft.csv"
OUT = ROOT / "evaluation" / "golden_human_60.csv"

# index -> (true_intent, escalate, reason, note)
FIX = {
    1: ("software_update", 0, "none", "iOS autocorrect I-bug, not other"),
    2: ("hardware_device", 1, "complaint_review", "Mac kernel panic + 3wks no machine + abuse -> escalate"),
    3: ("software_update", 1, "complaint_review", "profanity + useless phone -> complaint review"),
    4: ("software_update", 0, "none", "iOS11 keyboard bug ambiguous; software over hardware"),
    6: ("support_access_followup", 0, "none", "closure thanks; heuristic legal_safety was false positive"),
    8: ("support_access_followup", 0, "none", "short version answer to diagnostic, not new update issue"),
    10: ("hardware_device", 1, "complaint_review", "Watch dead after week + sarcasm caps"),
    14: ("purchase_billing_service", 0, "none", "iPhoneX delivery/order status"),
    15: ("support_access_followup", 0, "none", "heuristic legal_safety FP; vague follow-up -> clarify auto"),
    16: ("other_out_of_scope", 1, "unresolvable", "Spanish non-English v1 -> other + escalate"),
    17: ("hardware_device", 1, "legal_safety", "swollen battery damaging screen = safety risk + warranty"),
    20: ("software_update", 0, "none", "High Sierra copy/paste regression, not hardware"),
    21: ("connectivity", 0, "none", "heuristic legal_safety FP; intermittent BT follow-up"),
    22: ("other_out_of_scope", 1, "complaint_review", "vague glitch + profanity 3 days -> escalate"),
    23: ("apple_id_icloud", 0, "none", "server login Q answerable; legal_safety FP"),
    25: ("battery_power", 0, "none", "new iPhone8 won't turn on/charging = power"),
    26: ("connectivity", 0, "none", "No SIM/carrier, not restore"),
    29: ("other_out_of_scope", 1, "unresolvable", "Portuguese music-availability + non-English"),
    31: ("software_update", 0, "none", "iOS11 keyboard changing/sounds = update bug"),
    32: ("support_access_followup", 0, "none", "'No...' answer + store Q secondary; follow-up"),
    34: ("support_access_followup", 0, "none", "spec drop answering diagnostic, no issue stated"),
    35: ("support_access_followup", 0, "none", "solved + thanks closure, not new BT issue"),
    36: ("hardware_device", 1, "legal_safety", "CRITICAL: charger flame + burned finger; weak missed safety"),
    37: ("apps_media", 0, "none", "FB crash; legal_safety FP"),
    38: ("setup_transfer_restore", 1, "complaint_review", "2 restores + disappointed -> complaint"),
    41: ("support_access_followup", 0, "none", "solved-status update, not new update issue"),
    42: ("apps_media", 0, "none", "spam iMessages influx Q, not follow-up"),
    43: ("support_access_followup", 1, "unresolvable", "version + dead screenshot link -> clarify/escalate"),
    45: ("apps_media", 0, "none", "playback error in media app, not generic howto"),
    46: ("other_out_of_scope", 0, "none", "peer-to-peer help, not customer-to-brand request"),
    48: ("other_out_of_scope", 0, "none", "home-button feature request/joke"),
    49: ("support_access_followup", 0, "none", "praise/commendation closure"),
    50: ("other_out_of_scope", 1, "unresolvable", "'this problem'+dead link, no detail"),
    51: ("purchase_billing_service", 1, "complaint_review", "angry policy/cost complaint + Java compat"),
    52: ("purchase_billing_service", 1, "human_request", "talk-to + renew = billing + human"),
    54: ("support_access_followup", 0, "none", "'I will try that...' follow-up"),
    55: ("software_update", 0, "none", "post-11.1 notifications regression; legal_safety FP"),
    57: ("hardware_device", 0, "none", "charger wire breaking = hardware"),
    58: ("connectivity", 0, "none", "BT keyboard won't connect = connectivity"),
}

def main():
    df = pd.read_csv(SRC)
    df["human_intent"] = df["intent"]
    df["human_escalate"] = df["escalate"]
    df["human_reason"] = df["escalate_reason"]
    df["flipped"] = False
    df["note"] = ""
    for idx, (intent, esc, reason, note) in FIX.items():
        if idx < len(df):
            if df.loc[idx, "human_intent"] != intent:
                df.loc[idx, "flipped"] = True
            if df.loc[idx, "human_escalate"] != esc:
                df.loc[idx, "flipped"] = True
            df.loc[idx, "human_intent"] = intent
            df.loc[idx, "human_escalate"] = esc
            df.loc[idx, "human_reason"] = reason
            df.loc[idx, "note"] = note
    df.to_csv(OUT, index=False)
    print(f"wrote {len(df)} -> {OUT}, flips={df.flipped.sum()}")
    # agreement weak vs human (intent)
    from sklearn.metrics import cohen_kappa_score, accuracy_score
    print("intent weak-vs-human acc:", round(accuracy_score(df.intent, df.human_intent), 3),
          "kappa:", round(cohen_kappa_score(df.intent, df.human_intent), 3))
    print("esc weak-vs-human acc:", round(accuracy_score(df.escalate, df.human_escalate), 3),
          "kappa:", round(cohen_kappa_score(df.escalate, df.human_escalate), 3))

if __name__ == "__main__":
    main()
