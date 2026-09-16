"""Single BrandRetriever factory (P2-2 unification).

Canonical TF-IDF-NN retriever over data/indexes/<brand>/ + KB lookup from
data/processed/<brand>_kb.csv. backend/main.py and frontend/app.py both import
from here — previously each defined its own _BrandRetriever closure (tripled
logic, already drifting: tuple vs str lookup shapes).

scripts/run_virgin_eval.py keeps its own frozen VirginRetriever (eval repro
stability; identical query math, str-only lookup). src/hybrid_retrieval.py
wraps any base with .doc_ids + .lookup + .query() and normalizes both lookup
shapes, so it works with this class and the frozen eval copy.

NOTE (index skew, documented not fixed): build_virgin_index.clean() maps
URL->" url ", @handle->" user " before fit, but query() uses plain .lower()
(matching the frozen eval path). Changing the query path alone would fork
serve-vs-eval scores — any fix must rebuild the committed index AND re-freeze
results_human200.csv together.
"""
from pathlib import Path

from . import brands as brands_mod


class BrandRetriever:
    """TF-IDF vectorizer + brute-force cosine NN + KB text lookup."""

    def __init__(self, vec, nn, doc_ids, lookup):
        self.vec = vec
        self.nn = nn
        self.doc_ids = doc_ids
        # lookup: tweet_id -> (text, clean) tuple (serving shape). Eval-frozen
        # VirginRetriever uses str values; lookup_text() normalizes both.
        self.lookup = lookup or {}

    def lookup_text(self, tweet_id: str) -> str:
        try:
            v = (self.lookup or {}).get(str(tweet_id), "")
            if isinstance(v, (list, tuple)) and len(v) > 0:
                return str(v[0] or "")
            return str(v or "")
        except Exception:
            return ""

    def query(self, text: str, k: int = 5):
        Xq = self.vec.transform([(text or "").lower()])
        dist, idx = self.nn.kneighbors(Xq, n_neighbors=min(k, len(self.doc_ids)))
        out = []
        for d, j in zip(dist[0], idx[0]):
            tid = self.doc_ids[j]
            raw, clean = self.lookup.get(tid, ("", "")) if isinstance(
                self.lookup.get(tid), (list, tuple)) else (self.lookup.get(tid, ""), "")
            out.append({"tweet_id": tid, "distance": float(d),
                        "score": float(1 - d), "text": raw, "clean": clean})
        return out


def make_retriever_for_brand(brand: str):
    """Load per-brand TF-IDF index; legacy/apple fallback; else None.

    Read-only: never builds or modifies KB/classifier/golden (V-EVAL owns those).
    """
    from .retriever import Retriever as LegacyAppleRetriever

    b = (brand or brands_mod.DEFAULT_BRAND).lower().strip()
    if b not in brands_mod.BRANDS:
        b = brands_mod.DEFAULT_BRAND
    try:
        for index_dir in brands_mod.get_index_candidates(b):
            try:
                p = Path(index_dir)
                vec_p = p / "tfidf_vectorizer.pkl"
                nn_p = p / "nn_index.pkl"
                ids_p = p / "doc_ids.csv"
                if not (vec_p.exists() and nn_p.exists() and ids_p.exists()):
                    continue
                import joblib
                import pandas as pd
                vec = joblib.load(vec_p)
                nn = joblib.load(nn_p)
                ids = pd.read_csv(ids_p)
                if "tweet_id" in ids.columns:
                    doc_ids = ids["tweet_id"].astype(str).tolist()
                else:
                    doc_ids = ids.iloc[:, -1].astype(str).tolist()
                _repo_root = Path(__file__).resolve().parents[1]
                kb_cands = []
                if b == "virgin":
                    kb_cands = [_repo_root / "data" / "processed" / "virgin_kb.csv"]
                else:
                    kb_cands = [_repo_root / "data" / "processed" / "apple_kb.csv"]
                lookup: dict = {}
                for kb_path in kb_cands:
                    try:
                        if kb_path.exists():
                            kb = pd.read_csv(kb_path, usecols=["tweet_id", "text", "clean"])
                            lookup = {str(r.tweet_id): (r.text, r.clean) for r in kb.itertuples()}
                            break
                    except Exception:
                        continue
                return BrandRetriever(vec, nn, doc_ids, lookup)
            except Exception:
                continue
    except Exception:
        pass
    if b == "apple":
        try:
            return LegacyAppleRetriever()
        except Exception:
            return None
    return None
