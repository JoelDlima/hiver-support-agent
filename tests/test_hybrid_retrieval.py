"""Tests for Phase 1b items 1.5/1.6 (hybrid retrieval) + 1.7/1.8 (KB manifest)."""
import hashlib
import json
import os
from pathlib import Path

import pandas as pd

from scripts.run_virgin_eval import VirginRetriever
from src.hybrid_retrieval import (
    HybridVirginRetriever,
    attach_citation,
    is_hybrid_enabled,
    rrf_score,
)

QUERIES = [
    "my train is delayed, how do I claim delay repay",
    "change my advance ticket and get a refund",
    "is the 21:03 from Euston still running",
    "lost my bag on the train from Birmingham",
    "packed train, no seats, terrible service",
]

CITATION_KEYS = {"tweet_id", "rank", "bm25_score", "cosine_score",
                 "rrf_score", "above_threshold"}


def test_flag_defaults_off(monkeypatch):
    monkeypatch.delenv("VIRGIN_HYBRID", raising=False)
    assert is_hybrid_enabled() is False


def test_off_mode_parity_with_virgin_retriever(monkeypatch):
    monkeypatch.setenv("VIRGIN_HYBRID", "0")
    base = VirginRetriever()
    hybrid = HybridVirginRetriever(base=VirginRetriever())
    assert hybrid.enabled is False
    for q in QUERIES:
        assert hybrid.query(q, k=5) == base.query(q, k=5)


def test_rrf_k60_math():
    assert rrf_score(1, 1) == 2 / 61
    assert abs(rrf_score(1, k=60) - 1 / 61) < 1e-12
    assert rrf_score(1, 2, k=60) == 1 / 61 + 1 / 62


def test_citation_helper_fields():
    c = attach_citation("123", 1, bm25_score=2.5, cosine_score=0.3,
                        rrf=0.03, min_cosine=0.1, text="t")
    assert CITATION_KEYS <= set(c)
    assert (c["rank"], c["bm25_score"], c["cosine_score"]) == (1, 2.5, 0.3)
    assert c["above_threshold"] is True
    c2 = attach_citation("123", 2, bm25_score=1.0, cosine_score=None, rrf=0.01)
    assert c2["above_threshold"] is False  # missing cosine never passes


def test_on_mode_fused_ranking_with_citations(monkeypatch):
    monkeypatch.setenv("VIRGIN_HYBRID", "1")
    hybrid = HybridVirginRetriever()
    assert hybrid.enabled is True
    res = hybrid.query(QUERIES[0], k=5)
    assert len(res) == 5
    for i, hit in enumerate(res, start=1):
        assert CITATION_KEYS <= set(hit), set(hit)
        assert hit["rank"] == i
        assert hit["rrf_score"] > 0
    rrfs = [h["rrf_score"] for h in res]
    assert rrfs == sorted(rrfs, reverse=True)
    # Fusion draws on both stages: at least one hit carries each score type.
    assert any(h["bm25_score"] is not None for h in res)
    assert any(h["cosine_score"] is not None for h in res)
    assert all(isinstance(h["above_threshold"], bool) for h in res)


def test_on_mode_topk_differs_gracefully(monkeypatch):
    # ON mode must return valid top-k for every probe query (no crash path).
    monkeypatch.setenv("VIRGIN_HYBRID", "1")
    hybrid = HybridVirginRetriever()
    for q in QUERIES:
        res = hybrid.query(q, k=5)
        assert len(res) == 5
        assert [h["rank"] for h in res] == [1, 2, 3, 4, 5]


def test_kb_manifest():
    manifest_path = Path(os.environ.get(
        "VIRGIN_MANIFEST",
        r"C:\Hiver\evaluation\virgin\kb_manifest.json"))
    assert manifest_path.exists(), f"missing {manifest_path} — run scripts/build_virgin_manifest.py"
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    for key in ("n_rows", "rows", "corpus_fingerprint_sha256", "counts",
                "quality", "params", "git_sha"):
        assert key in m, key
    for key in ("exact_dup_rate", "near_dup_rate_estimate", "boilerplate_share",
                "non_english_share", "url_rate"):
        assert key in m["quality"], key
        assert 0.0 <= m["quality"][key] <= 1.0
    assert len(m["corpus_fingerprint_sha256"]) == 64

    kb = pd.read_csv(r"C:\Hiver\data\processed\virgin_kb.csv", usecols=["tweet_id", "text"])
    assert m["n_rows"] == len(kb) == len(m["rows"])
    # Spot-check per-row hashes recompute from the CSV.
    for i in (0, len(kb) // 2, len(kb) - 1):
        expect = hashlib.sha256(str(kb.text.iloc[i]).encode("utf-8")).hexdigest()
        assert m["rows"][i]["content_sha256"] == expect
        assert m["rows"][i]["tweet_id"] == str(kb.tweet_id.iloc[i])
    # Fingerprint recomputes from sorted row hashes.
    fp = hashlib.sha256(
        "\n".join(sorted(r["content_sha256"] for r in m["rows"])).encode("utf-8")
    ).hexdigest()
    assert m["corpus_fingerprint_sha256"] == fp
