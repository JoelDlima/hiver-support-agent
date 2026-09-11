"""Build 50-item second-annotator pack: spotcheck_30 (annotator-1 done) + 20 fresh draws
(seed 11, excluding golden + spotcheck texts). Output evaluation/virgin/annotation_pack_50.csv
with EMPTY label columns for annotator 2. No key needed.
"""
import pandas as pd
from pathlib import Path

VIRGIN_DIR = Path(r"C:\Hiver\evaluation\virgin")
POOL = Path(r"C:\Hiver\data\processed\virgin_inbound_pool.csv")


def main():
    spot = pd.read_csv(VIRGIN_DIR / "spotcheck_30.csv")
    gold = pd.read_csv(VIRGIN_DIR / "golden_human_200.csv")
    pool = pd.read_csv(POOL, usecols=["text"]).dropna().drop_duplicates()
    seen = set(spot.text.tolist()) | set(gold.text.tolist())
    fresh = pool[~pool.text.isin(seen)].sample(20, random_state=11).reset_index(drop=True)
    pack = pd.concat([
        spot[["text"]].assign(source="spotcheck_30"),
        fresh.assign(source="fresh_seed11"),
    ], ignore_index=True)
    pack.insert(0, "pack_idx", range(len(pack)))
    pack["human_intent"] = ""
    pack["human_escalate"] = ""
    pack["human_reason"] = ""
    out = VIRGIN_DIR / "annotation_pack_50.csv"
    pack.to_csv(out, index=False)
    print(f"wrote {len(pack)} (30 spotcheck + 20 fresh) -> {out}")
    print("Annotator 2 fills human_intent / human_escalate / human_reason per docs/ANNOTATION_PROTOCOL.md §1")


if __name__ == "__main__":
    main()
