"""Build Apple KB: outbound AppleSupport replies deduped + inbound Apple threads sample."""
import csv
from pathlib import Path
import pandas as pd
from src.text_norm import normalize

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "twcs.csv"
PROC = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)

def main():
    print("loading raw (usecols)...")
    df = pd.read_csv(RAW, usecols=["tweet_id", "author_id", "inbound", "text"])
    # Outbound Apple KB
    out = df[(df.author_id == "AppleSupport")].copy()
    out["clean"] = out.text.fillna("").map(normalize)
    out = out[out.clean.str.len() > 10]
    # Template cap: cap exact-clean duplicates at K=5
    out["rank"] = out.groupby("clean").cumcount()
    out = out[out["rank"] < 5].drop(columns=["rank"])
    out.to_csv(PROC / "apple_kb.csv", index=False)
    print(f"KB: {len(out)} rows -> {PROC/'apple_kb.csv'}")
    # Inbound Apple pool (mention AppleSupport or threaded) — approximate via mention
    inbound = df[df.text.str.contains("@AppleSupport", case=False, na=False)].copy()
    inbound["clean"] = inbound.text.fillna("").map(normalize)
    inbound = inbound[inbound.clean.str.len() > 10]
    inbound.to_csv(PROC / "apple_inbound_pool.csv", index=False)
    print(f"Inbound pool: {len(inbound)} rows")

if __name__ == "__main__":
    main()
