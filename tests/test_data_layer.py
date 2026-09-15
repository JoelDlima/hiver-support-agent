"""Phase 2C data-layer tests: parquet round-trip, manifest fingerprint,
thread orphans, AL candidate mix. Reads NEW artifacts only; never writes.
Fail-closed with actionable messages (tells which builder script to run)."""

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
KB_PQ = ROOT / "data/processed/virgin_kb.parquet"
POOL_PQ = ROOT / "data/processed/virgin_inbound_pool.parquet"
THREADS_PQ = ROOT / "data/processed/virgin_threads.parquet"
THREADS_MD = ROOT / "evaluation/virgin/threads_report.md"
AL_CSV = ROOT / "evaluation/virgin/al_candidates_300.csv"
MANIFEST = ROOT / "evaluation/virgin/kb_manifest.json"
POOL_CSV = ROOT / "data/processed/virgin_inbound_pool.csv"


def _require(path: Path) -> Path:
    assert path.exists(), f"MISSING {path} — run the Phase 2C builder scripts first"
    return path


def test_parquet_round_trip_row_counts():
    kb = pd.read_parquet(_require(KB_PQ))
    pool = pd.read_parquet(_require(POOL_PQ))
    assert len(kb) == 27172, len(kb)
    assert len(pool) == 37444, len(pool)
    for df in (kb, pool):
        for col in ("tweet_id", "text", "created_at", "brand"):
            assert col in df.columns, f"missing col {col} in {df.columns.tolist()}"
        assert (df["brand"] == "virgin").all()
        non_null = df.dropna(subset=["created_at"])
        assert non_null["created_at"].is_monotonic_increasing, \
            "parquet not sorted by created_at"


def test_manifest_fingerprint_still_verifies():
    kb = pd.read_parquet(_require(KB_PQ))
    hashes = [hashlib.sha256((t or "").encode("utf-8")).hexdigest()
              for t in kb["text"].tolist()]
    fp = hashlib.sha256("\n".join(sorted(hashes)).encode("utf-8")).hexdigest()
    manifest = json.loads(_require(MANIFEST).read_text(encoding="utf-8"))
    assert fp == manifest["corpus_fingerprint_sha256"], \
        "parquet content diverged from manifest fingerprint"
    assert manifest["n_rows"] == len(kb) == 27172


def test_thread_orphans_logged():
    th = pd.read_parquet(_require(THREADS_PQ))
    md = _require(THREADS_MD).read_text(encoding="utf-8")
    assert len(th) > 0
    assert "orphan" in th.columns and th["orphan"].dtype == bool
    rate = float(th["orphan"].mean())
    assert 0.0 <= rate < 1.0
    for token in ("orphan", "thread", "dialog"):
        assert token in md.lower(), f"threads_report.md missing '{token}'"
    assert f"{rate:.4f}" in md, "orphan rate not logged in report"
    assert th["thread_size"].ge(1).all()
    assert int((th["thread_size"] >= 2).sum()) > 0, "no multi-turn threads found"


def test_al_csv_has_300_rows_with_strategy_mix():
    al = pd.read_csv(_require(AL_CSV))
    assert len(al) == 300, len(al)
    assert "query_strategy" in al.columns
    mix = al["query_strategy"].value_counts().to_dict()
    assert mix == {"margin": 150, "diversity": 100, "rare_intent": 50}, mix
    assert al["tweet_id"].nunique() == 300, "duplicate tweet_ids in AL candidates"
    pool_ids = set(pd.read_csv(POOL_CSV, usecols=["tweet_id"])["tweet_id"].tolist())
    assert set(al["tweet_id"].tolist()) <= pool_ids, \
        "AL candidates outside inbound pool"
