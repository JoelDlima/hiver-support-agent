"""Build VirginTrains KB: outbound VirginTrains replies deduped + inbound mention pool.

Mirrors scripts/build_kb.py (Apple) for the VirginTrains brand.
- Source: C:\\Hiver\\data\\raw\\twcs.csv (PS strict: TWCS only)
- Outbound: author_id == "VirginTrains", clean len > 10, template-cap K=5
- Inbound pool: case-insensitive @VirginTrains mention, clean len > 10
- Outputs: data/processed/virgin_kb.csv + data/processed/virgin_inbound_pool.csv
"""
import pandas as pd
from pathlib import Path
from src.text_norm import normalize

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "twcs.csv"
PROC = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)

OUTBOUND_AUTHOR = "VirginTrains"
MENTION = "@VirginTrains"
TEMPLATE_CAP = 5


def main():
    print("loading raw (usecols)...")
    df = pd.read_csv(RAW, usecols=["tweet_id", "author_id", "inbound", "text"])
    print(f"raw rows: {len(df)}")
    # Outbound Virgin KB
    out = df[df.author_id == OUTBOUND_AUTHOR].copy()
    print(f"outbound raw: {len(out)}")
    out["clean"] = out.text.fillna("").map(normalize)
    out = out[out.clean.str.len() > 10]
    print(f"outbound len>10: {len(out)}")
    # Template cap: cap exact-clean duplicates at K=5
    out["rank"] = out.groupby("clean").cumcount()
    out = out[out["rank"] < TEMPLATE_CAP].drop(columns=["rank"])
    out.to_csv(PROC / "virgin_kb.csv", index=False)
    print(f"KB: {len(out)} rows -> {PROC / 'virgin_kb.csv'}")
    # Inbound mention pool
    inbound = df[df.text.str.contains(MENTION, case=False, na=False)].copy()
    print(f"mention raw: {len(inbound)}")
    inbound["clean"] = inbound.text.fillna("").map(normalize)
    inbound = inbound[inbound.clean.str.len() > 10]
    inbound.to_csv(PROC / "virgin_inbound_pool.csv", index=False)
    print(f"Inbound pool: {len(inbound)} rows -> {PROC / 'virgin_inbound_pool.csv'}")
    # Stats
    print(f"STATS outbound={len(out)} inbound_pool={len(inbound)} "
          f"kb_dedup_cap={TEMPLATE_CAP} brand={OUTBOUND_AUTHOR}")


if __name__ == "__main__":
    main()
