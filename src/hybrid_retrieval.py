"""Hybrid BM25 + TF-IDF-NN retrieval over the VirginTrains KB (Phase 1b, item 1.5).

Stage-1: BM25 (rank-bm25, Okapi) over KB texts.
Stage-2: Reciprocal Rank Fusion (RRF, k=60) of the BM25 ranking with the
existing TF-IDF-NN ranking (data/indexes/virgin, see scripts/build_virgin_index.py).

Flag-gated via env VIRGIN_HYBRID (default "0" = OFF):
- OFF: query() delegates directly to VirginRetriever.query() — behavior
  identical to the current retriever (same call, same return objects).
- ON: fused BM25 + TF-IDF-NN ranking with per-passage citation fields
  (see attach_citation, item 1.6).

No changes to the current retriever; this module only wraps it.
"""

import os

RRF_K = 60
BM25_TOPN_DEFAULT = 100
TFIDF_TOPN_DEFAULT = 100

_TRUE_VALUES = {"1", "true", "yes", "on"}


def is_hybrid_enabled() -> bool:
    """True iff VIRGIN_HYBRID env var is a truthy value. Default OFF."""
    return os.getenv("VIRGIN_HYBRID", "0").strip().lower() in _TRUE_VALUES


def tokenize(text: str) -> list:
    """BM25 tokenizer: lowercase + whitespace split.

    Mirrors the lowercasing applied on both sides of the TF-IDF path
    (build_virgin_index.clean lowercases docs; VirginRetriever.query
    lowercases the query), so both stages see the same case folding.
    """
    return (text or "").lower().split()


def rrf_score(*ranks: int, k: int = RRF_K) -> float:
    """Reciprocal Rank Fusion score: sum(1 / (k + rank)) over 1-indexed ranks."""
    return sum(1.0 / (k + r) for r in ranks)


def attach_citation(tweet_id: str, rank: int, bm25_score=None,
                    cosine_score=None, rrf: float = 0.0,
                    min_cosine: float = 0.0, text: str = "",
                    clean: str = "", distance=None) -> dict:
    """Score-attached citation helper (item 1.6) for UI display.

    Fields per passage: rank (1-indexed fused rank), bm25_score (BM25 stage-1
    score, None if absent from the BM25 shortlist), cosine_score (TF-IDF-NN
    cosine = 1 - distance, None if absent from the TF-IDF shortlist),
    rrf_score (fusion score), above_threshold (cosine >= min_cosine flag).
    """
    return {
        "tweet_id": str(tweet_id),
        "rank": int(rank),
        "bm25_score": None if bm25_score is None else float(bm25_score),
        "cosine_score": None if cosine_score is None else float(cosine_score),
        "rrf_score": float(rrf),
        "above_threshold": bool(cosine_score is not None and cosine_score >= min_cosine),
        "text": text,
        "clean": clean,
        "distance": None if distance is None else float(distance),
        # 'score' keeps the VirginRetriever cosine convention for UI compat
        # (None when the passage came only from the BM25 stage).
        "score": None if cosine_score is None else float(cosine_score),
    }


class HybridVirginRetriever:
    """Virgin KB retriever with optional BM25+RRF fusion.

    Args:
        base: existing VirginRetriever instance (created lazily if None).
        rrf_k: RRF constant (default 60).
        bm25_topn: BM25 stage-1 shortlist depth.
        tfidf_topn: TF-IDF-NN shortlist depth used for fusion (ON mode only).
        min_cosine: cosine threshold for the citation above_threshold flag.
    """

    def __init__(self, base=None, rrf_k: int = RRF_K,
                 bm25_topn: int = BM25_TOPN_DEFAULT,
                 tfidf_topn: int = TFIDF_TOPN_DEFAULT,
                 min_cosine: float = 0.0):
        if base is None:
            from scripts.run_virgin_eval import VirginRetriever
            base = VirginRetriever()
        self._base = base
        self.enabled = is_hybrid_enabled()
        self.rrf_k = rrf_k
        self.bm25_topn = bm25_topn
        self.tfidf_topn = tfidf_topn
        self.min_cosine = min_cosine
        self._bm25 = None  # built lazily, ON-mode only (OFF stays identical + fast)

    def _ensure_bm25(self):
        if self._bm25 is None:
            from rank_bm25 import BM25Okapi
            corpus = [tokenize(self._base.lookup.get(tid, ""))
                      for tid in self._base.doc_ids]
            self._bm25 = BM25Okapi(corpus)
        return self._bm25

    def query(self, text: str, k: int = 5) -> list:
        if not self.enabled:
            # OFF: identical behavior to the current retriever.
            return self._base.query(text, k=k)
        return self._query_fused(text, k=k)

    def _query_fused(self, text: str, k: int = 5) -> list:
        doc_ids = self._base.doc_ids
        n = len(doc_ids)
        depth_tfidf = min(self.tfidf_topn, n)
        depth_bm25 = min(self.bm25_topn, n)

        tfidf_hits = self._base.query(text, k=depth_tfidf)
        tfidf_rank = {}
        tfidf_cos = {}
        tfidf_dist = {}
        for pos, h in enumerate(tfidf_hits, start=1):
            tfidf_rank.setdefault(h["tweet_id"], pos)
            tfidf_cos.setdefault(h["tweet_id"], h["score"])
            tfidf_dist.setdefault(h["tweet_id"], h["distance"])

        bm25 = self._ensure_bm25()
        import numpy as np
        scores = np.asarray(bm25.get_scores(tokenize(text)), dtype=float)
        top_idx = np.argsort(-scores, kind="stable")[:depth_bm25]
        bm25_rank = {}
        bm25_val = {}
        for pos, j in enumerate(top_idx.tolist(), start=1):
            tid = doc_ids[j]
            if tid not in bm25_rank:  # keep best rank on duplicate ids
                bm25_rank[tid] = pos
                bm25_val[tid] = float(scores[j])

        fused = []
        for tid in set(bm25_rank) | set(tfidf_rank):
            ranks = []
            if tid in bm25_rank:
                ranks.append(bm25_rank[tid])
            if tid in tfidf_rank:
                ranks.append(tfidf_rank[tid])
            fused.append((tid, rrf_score(*ranks, k=self.rrf_k)))
        # Deterministic tie-break on tweet_id.
        fused.sort(key=lambda t: (-t[1], t[0]))

        out = []
        for rank, (tid, rrf) in enumerate(fused[:k], start=1):
            out.append(attach_citation(
                tid, rank,
                bm25_score=bm25_val.get(tid),
                cosine_score=tfidf_cos.get(tid),
                rrf=rrf,
                min_cosine=self.min_cosine,
                text=self._base.lookup.get(tid, ""),
                clean="",
                distance=tfidf_dist.get(tid),
            ))
        return out
