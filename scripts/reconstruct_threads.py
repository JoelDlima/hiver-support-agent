"""Reconstruct VirginTrains conversation threads from the raw TWCS dump (Phase 2C).

Method (follows the TweetSumm EMNLP'21 setup: reply-tree reconstruction from
in_response_to_tweet_id links, children ordered by created_at):
  1. Virgin subset of data/raw/twcs.csv = rows where author_id == "VirginTrains"
     OR text contains "@VirginTrains" (case-insensitive). READ-ONLY; raw never
     modified.
  2. Structural threads: recursive/iterative walk up in_response_to_tweet_id to
     the root tweet (memoised, cycle-guarded). A link whose parent id is absent
     from the Virgin subset quarantines the tweet as an ORPHAN (it becomes its
     own thread root with orphan=True; orphan rate is logged, never silently
     dropped).
  3. Sibling order: every thread sorted by created_at (NaT last, then tweet_id).
  4. 7-day gap rule: within a structural thread, a consecutive created_at gap
     > 7 days splits the thread (later segment gets a new thread_id rooted at
     its first tweet; gap_split=True on that tweet, gap_splits counter logged).
  5. depth = reply-chain distance from the final thread root following parent
     links while the parent stays in the same thread (0 for roots / orphans);
     position_in_thread = created_at order index; thread_size per thread.

Writes (NEW files only):
  data/processed/virgin_threads.parquet
  evaluation/virgin/threads_report.md   (dialog counts, orphan rate, gap splits)

Usage:
  C:\\Hiver\\.venv\\Scripts\\python.exe C:\\Hiver\\scripts\\reconstruct_threads.py
"""

import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/twcs.csv"
OUT_PQ = ROOT / "data/processed/virgin_threads.parquet"
OUT_MD = ROOT / "evaluation/virgin/threads_report.md"

BRAND_AUTHOR = "VirginTrains"
MENTION = "@VirginTrains"
GAP_SPLIT = pd.Timedelta(days=7)
CREATED_AT_FMT = "%a %b %d %H:%M:%S %z %Y"
CHUNKSIZE = 200_000


def load_virgin_subset() -> pd.DataFrame:
    """Chunked read of raw; keeps only Virgin-related rows."""
    t0 = time.perf_counter()
    parts = []
    total = 0
    for ch in pd.read_csv(
        RAW,
        usecols=["tweet_id", "author_id", "inbound", "created_at", "text",
                 "response_tweet_id", "in_response_to_tweet_id"],
        chunksize=CHUNKSIZE,
    ):
        total += len(ch)
        mask = (ch["author_id"] == BRAND_AUTHOR) | ch["text"].str.contains(
            MENTION, case=False, na=False
        )
        parts.append(ch[mask])
    df = pd.concat(parts, ignore_index=True)
    df["tweet_id"] = df["tweet_id"].astype("int64")
    df["created_at"] = pd.to_datetime(
        df["created_at"], format=CREATED_AT_FMT, utc=True, errors="coerce"
    )
    print(f"virgin subset: {len(df)} / {total} raw rows "
          f"in {time.perf_counter() - t0:.1f}s")
    return df


def find_roots(df: pd.DataFrame) -> pd.Series:
    """Walk each tweet's in_response_to chain to its structural root.

    Returns (root_id, orphan) per row. Parent absent from subset (or NaN-side
    termination) -> root is self; orphan=True iff the tweet named a parent id
    that is not in the subset. Cycles break at the smallest tweet_id in the
    loop (deterministic).
    """
    ids = set(df["tweet_id"].tolist())
    parent_of = dict(zip(df["tweet_id"].tolist(),
                         df["in_response_to_tweet_id"].tolist()))
    root_cache: dict = {}

    def root(tid: int) -> int:
        seen = []
        cur = tid
        while True:
            if cur in root_cache:
                r = root_cache[cur]
                for s in seen:
                    root_cache[s] = r
                return r
            if cur in seen:  # cycle: deterministic break
                r = min(seen)
                for s in seen:
                    root_cache[s] = r
                return r
            seen.append(cur)
            p = parent_of.get(cur)
            if p is None or (isinstance(p, float) and pd.isna(p)):
                for s in seen:
                    root_cache[s] = cur
                return cur
            try:
                p = int(p)
            except (TypeError, ValueError):
                for s in seen:
                    root_cache[s] = cur
                return cur
            if p not in ids:  # dangling parent -> quarantine at self's chain head
                for s in seen:
                    root_cache[s] = cur
                return cur
            cur = p

    roots, orphans = [], []
    for tid in df["tweet_id"].tolist():
        r = root(tid)
        roots.append(r)
        p = parent_of.get(tid)
        orphans.append(
            r == tid and p is not None
            and not (isinstance(p, float) and pd.isna(p))
        )
    return pd.Series(roots, index=df.index, name="thread_id"), \
        pd.Series(orphans, index=df.index, name="orphan")


def main() -> None:
    if not RAW.exists():
        raise SystemExit(f"MISSING {RAW}")
    t0 = time.perf_counter()
    df = load_virgin_subset()
    df["thread_id"], df["orphan"] = find_roots(df)
    n_orphans = int(df["orphan"].sum())
    print(f"structural threads: {df['thread_id'].nunique()} "
          f"orphans quarantined: {n_orphans} ({n_orphans / len(df):.4f})")

    # created_at sibling sort, then 7-day gap splits within structural threads.
    df = df.sort_values(["thread_id", "created_at", "tweet_id"]).reset_index(drop=True)
    df["gap_split"] = False
    final_tids = df["thread_id"].tolist()
    prev_ts, prev_tid = None, None
    n_gap_splits = 0
    for i, row in df.iterrows():
        if row["thread_id"] == prev_tid and pd.notna(row["created_at"]) \
                and pd.notna(prev_ts) and row["created_at"] - prev_ts > GAP_SPLIT:
            final_tids[i] = int(row["tweet_id"])  # new thread rooted here
            df.at[i, "gap_split"] = True
            n_gap_splits += 1
        prev_ts, prev_tid = row["created_at"], final_tids[i]
    df["thread_id"] = final_tids

    # Final ordering + positions + depths.
    df = df.sort_values(["thread_id", "created_at", "tweet_id"]).reset_index(drop=True)
    df["thread_size"] = df.groupby("thread_id")["thread_id"].transform("size")
    df["position_in_thread"] = df.groupby("thread_id").cumcount()
    in_thread = set(zip(df["thread_id"].tolist(), df["tweet_id"].tolist()))
    par = dict(zip(df["tweet_id"].tolist(),
                   df["in_response_to_tweet_id"].tolist()))
    tid_thread = dict(zip(df["tweet_id"].tolist(), df["thread_id"].tolist()))

    def depth(tid: int) -> int:
        d, cur, guard = 0, tid, 0
        while guard < 1000:
            p = par.get(cur)
            if p is None or (isinstance(p, float) and pd.isna(p)):
                return d
            try:
                p = int(p)
            except (TypeError, ValueError):
                return d
            if tid_thread.get(p) != tid_thread.get(tid):
                return d
            d, cur, guard = d + 1, p, guard + 1
        return d

    df["depth"] = [depth(t) for t in df["tweet_id"].tolist()]
    df["brand"] = "virgin"

    cols = ["thread_id", "tweet_id", "author_id", "inbound", "created_at", "text",
            "in_response_to_tweet_id", "response_tweet_id", "brand",
            "orphan", "gap_split", "depth", "position_in_thread", "thread_size"]
    df = df[cols]
    df.to_parquet(OUT_PQ, engine="pyarrow", compression="zstd",
                  row_group_size=128 * 1024, index=False)

    # ---- dialog counts for the report ----
    n_threads = int(df["thread_id"].nunique())
    sizes = df.groupby("thread_id").size()
    singletons = int((sizes == 1).sum())
    multi = n_threads - singletons
    # A "dialog" = thread with >=2 turns spanning both sides (inbound + brand reply).
    g = df.groupby("thread_id")["inbound"].agg(["size", "nunique"])
    dialogs = int(((g["size"] >= 2) & (g["nunique"] >= 2)).sum())
    depth_hist = df["depth"].value_counts().sort_index().head(10)
    dmin, dmax = df["created_at"].min(), df["created_at"].max()

    report = f"""# VirginTrains thread reconstruction report

Source: `data/raw/twcs.csv` (READ-ONLY) — Virgin subset: `author_id == "VirginTrains"`
OR text mentions `@VirginTrains` (case-insensitive).
Method: recursive `in_response_to_tweet_id` walk to root (memoised, cycle-guarded),
`created_at` sibling sort, 7-day gap split, orphan quarantine.
Output: `data/processed/virgin_threads.parquet` ({len(df)} rows, ZSTD).

## Thread stats

| metric | value |
|---|---|
| virgin tweets | {len(df)} |
| threads | {n_threads} |
| singleton threads | {singletons} ({singletons / n_threads:.3f}) |
| multi-turn threads | {multi} |
| dialogs (>=2 turns, both inbound+reply) | {dialogs} |
| avg thread size | {len(df) / n_threads:.2f} |
| max thread size | {int(sizes.max())} |
| max depth | {int(df['depth'].max())} |
| orphans quarantined | {n_orphans} (orphan rate {n_orphans / len(df):.4f}) |
| 7-day gap splits | {n_gap_splits} |
| date range | {dmin} .. {dmax} |

## Depth histogram (depth: count)

"""
    for d, c in depth_hist.items():
        report += f"- depth {int(d)}: {int(c)}\n"
    report += f"\nBuilt in {time.perf_counter() - t0:.1f}s.\n"
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(report, encoding="utf-8")

    print(f"threads={n_threads} singletons={singletons} multi={multi} "
          f"dialogs={dialogs} orphans={n_orphans} "
          f"({n_orphans / len(df):.4f}) gap_splits={n_gap_splits} "
          f"maxdepth={int(df['depth'].max())}")
    print(f"wrote {OUT_PQ} + {OUT_MD}")


if __name__ == "__main__":
    main()
