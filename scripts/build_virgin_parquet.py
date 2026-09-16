"""Build processed parquet data layer for VirginTrains (Phase 2C).

Reads (READ-ONLY — never modified):
  data/processed/virgin_kb.csv            (27,172 rows, cols: tweet_id,author_id,inbound,text,clean)
  data/processed/virgin_inbound_pool.csv  (37,444 rows, same cols)
  data/raw/twcs.csv                       (usecols tweet_id,created_at only, for enrichment)

Writes (NEW files only):
  data/processed/virgin_kb.parquet
  data/processed/virgin_inbound_pool.parquet

Format: pyarrow parquet, ZSTD compression, row_group_size=128k (131072 rows),
sorted by created_at, then brand, then tweet_id (deterministic).

Enrichment: tweet_id LEFT JOIN onto raw created_at + constant brand="virgin".
The virgin CSVs carry no created_at/brand of their own; joining raw keeps the
layer self-describing for thread reconstruction and time-based splits without
touching the source CSVs.

Prints: per-file CSV vs parquet bytes, read timings (CSV vs parquet), speedup,
row counts, and a manifest-fingerprint check (sha256 over raw `text`, same
definition as scripts/build_virgin_manifest.py) so the parquet layer provably
preserves corpus content.

Usage:
  .venv\\Scripts\\python.exe scripts\\build_virgin_parquet.py
"""

import hashlib
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
KB_CSV = ROOT / "data/processed/virgin_kb.csv"
POOL_CSV = ROOT / "data/processed/virgin_inbound_pool.csv"
RAW = ROOT / "data/raw/twcs.csv"
KB_PQ = ROOT / "data/processed/virgin_kb.parquet"
POOL_PQ = ROOT / "data/processed/virgin_inbound_pool.parquet"

ROW_GROUP_SIZE = 128 * 1024  # 128k rows per row group
BRAND = "virgin"
CREATED_AT_FMT = "%a %b %d %H:%M:%S %z %Y"  # e.g. "Tue Oct 31 22:10:47 +0000 2017"


def content_fingerprint(texts) -> str:
    hashes = [hashlib.sha256((t or "").encode("utf-8")).hexdigest() for t in texts]
    return hashlib.sha256("\n".join(sorted(hashes)).encode("utf-8")).hexdigest()


def load_created_at_map() -> pd.DataFrame:
    """tweet_id -> created_at (UTC) from raw TWCS dump, read with usecols only."""
    t0 = time.perf_counter()
    raw = pd.read_csv(RAW, usecols=["tweet_id", "created_at"])
    raw["created_at"] = pd.to_datetime(
        raw["created_at"], format=CREATED_AT_FMT, utc=True, errors="coerce"
    )
    print(f"raw created_at map: {len(raw)} rows in {time.perf_counter() - t0:.1f}s, "
          f"nat={int(raw['created_at'].isna().sum())}")
    return raw


def convert(csv_path: Path, pq_path: Path, created_at_map: pd.DataFrame) -> dict:
    t0 = time.perf_counter()
    df = pd.read_csv(csv_path)
    csv_read_s = time.perf_counter() - t0
    n_csv = len(df)

    df["tweet_id"] = df["tweet_id"].astype("int64")
    df = df.merge(created_at_map, on="tweet_id", how="left")
    n_missing_ts = int(df["created_at"].isna().sum())
    df["brand"] = BRAND
    # Deterministic time-major order; NaT (if any) sorts last.
    df = df.sort_values(
        ["created_at", "brand", "tweet_id"], na_position="last"
    ).reset_index(drop=True)

    t1 = time.perf_counter()
    df.to_parquet(
        pq_path, engine="pyarrow", compression="zstd",
        row_group_size=ROW_GROUP_SIZE, index=False,
    )
    pq_write_s = time.perf_counter() - t1

    # Read-back benchmark (the "speedup vs CSV" number).
    t2 = time.perf_counter()
    back = pd.read_parquet(pq_path)
    pq_read_s = time.perf_counter() - t2
    assert len(back) == n_csv, f"round-trip row mismatch: {len(back)} != {n_csv}"

    import pyarrow.parquet as pq
    meta = pq.read_metadata(pq_path)
    enc = {meta.row_group(i).column(j).compression
           for i in range(meta.num_row_groups) for j in range(meta.num_columns)}

    csv_bytes = csv_path.stat().st_size
    pq_bytes = pq_path.stat().st_size
    stats = {
        "name": csv_path.name,
        "n_rows": n_csv,
        "n_cols": df.shape[1],
        "csv_bytes": csv_bytes,
        "pq_bytes": pq_bytes,
        "size_ratio": round(csv_bytes / pq_bytes, 2) if pq_bytes else 0.0,
        "csv_read_s": round(csv_read_s, 2),
        "pq_read_s": round(pq_read_s, 3),
        "read_speedup": round(csv_read_s / pq_read_s, 1) if pq_read_s > 0 else 0.0,
        "pq_write_s": round(pq_write_s, 2),
        "missing_created_at": n_missing_ts,
        "row_groups": meta.num_row_groups,
        "encodings": sorted(str(e) for e in enc),
        "fingerprint": content_fingerprint(df["text"].tolist()),
        "sorted_ok": bool(
            df["created_at"].is_monotonic_increasing or df["created_at"].isna().any()
            and df.dropna(subset=["created_at"])["created_at"].is_monotonic_increasing
        ),
    }
    return stats


def main() -> None:
    for p in (KB_CSV, POOL_CSV, RAW):
        if not p.exists():
            raise SystemExit(f"MISSING {p}")
    created_at_map = load_created_at_map()

    results = [
        convert(KB_CSV, KB_PQ, created_at_map),
        convert(POOL_CSV, POOL_PQ, created_at_map),
    ]

    import json
    manifest = json.loads(
        (ROOT / "evaluation/virgin/kb_manifest.json").read_text(encoding="utf-8")
    )
    print("\n== Virgin parquet data layer ==")
    for s in results:
        print(f"-- {s['name']} -> {Path(s['name']).stem + '.parquet'}")
        print(f"   rows={s['n_rows']} cols={s['n_cols']} "
              f"csv={s['csv_bytes'] / 1e6:.2f}MB pq={s['pq_bytes'] / 1e6:.2f}MB "
              f"size_ratio={s['size_ratio']}x row_groups={s['row_groups']} "
              f"codecs={s['encodings']}")
        print(f"   read: csv={s['csv_read_s']}s parquet={s['pq_read_s']}s "
              f"speedup={s['read_speedup']}x (write {s['pq_write_s']}s)")
        print(f"   missing_created_at={s['missing_created_at']} sorted_ok={s['sorted_ok']}")
        print(f"   content_sha fingerprint={s['fingerprint'][:16]}...")
    kb_fp = results[0]["fingerprint"]
    print(f"manifest fingerprint verifies: "
          f"{kb_fp == manifest['corpus_fingerprint_sha256']} "
          f"(manifest n_rows={manifest['n_rows']})")


if __name__ == "__main__":
    main()
