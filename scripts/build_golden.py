"""Build golden eval set: 200 stratified + documented sampling. Human-reviewable CSV."""
import pandas as pd
from pathlib import Path
from src import classifier as clf_mod
from src.text_norm import features_for_escalation

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "data" / "processed" / "apple_inbound_pool.csv"
OUT = ROOT / "evaluation" / "golden_v1.csv"
OUT.parent.mkdir(parents=True, exist_ok=True)

# Heuristic escalate label for golden draft (human must review/override)
def heuristic_escalate(text, intent, conf=0.6):
    f = features_for_escalation(text)
    if f["has_legal_safety"]:
        return 1, "legal_safety"
    if f["has_account_security"] or f["has_data_loss"]:
        return 1, "account_security"
    if f["has_human_request"]:
        return 1, "human_request"
    if f["is_link_only"] or f["is_very_short"] and intent == "other_out_of_scope":
        return 1, "unresolvable"
    return 0, "none"

def main(n=200, seed=7):
    df = pd.read_csv(POOL, usecols=["text"]).dropna().drop_duplicates()
    df["weak_intent"] = df.text.map(clf_mod.weak_label)
    # Stratify: ~16-18 per intent (11 intents)
    parts = []
    per = n // 11
    for intent, g in df.groupby("weak_intent"):
        parts.append(g.sample(min(per + 2, len(g)), random_state=seed))
    gold = pd.concat(parts).sample(frac=1, random_state=seed).head(n).reset_index(drop=True)
    gold["intent"] = gold["weak_intent"]  # human to verify; pre-filled
    esc = [heuristic_escalate(t, i) for t, i in zip(gold.text, gold.intent)]
    gold["escalate"] = [e for e, _ in esc]
    gold["escalate_reason"] = [r for _, r in esc]
    gold["needs_review"] = True
    gold[["text", "intent", "escalate", "escalate_reason"]].to_csv(OUT, index=False)
    print(f"golden {len(gold)} -> {OUT}")
    print(gold.intent.value_counts().to_string())
    print("escalate rate:", round(gold.escalate.mean(), 3))
    print("NOTE: weak labels are drafts — reviewer must flip wrong intents; record flips for judge-agreement study.")

if __name__ == "__main__":
    main()
