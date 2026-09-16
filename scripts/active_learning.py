"""Active-learning candidate selection over the Virgin inbound pool (Phase 2C).

Strategy (all logic vendored — no modAL / no new dependencies):
  1. margin (150): smallest P(top1) - P(top2) under models/intent_virgin.pkl
     (TF-IDF LogReg). Margin sampling: most uncertain first.
  2. diversity (100): k-means (k=100, seed 42) over pool embeddings, one
     nearest-to-centroid pick per cluster, skipping margin picks (next-nearest
     fill). Embeddings = MiniLM (all-MiniLM-L6-v2) ONLY if sentence_transformers
     AND torch are already installed; otherwise TF-IDF. torch is NEVER installed
     here (CPU-only, offline-tolerant rule).
  3. rare_intent (50): from the remaining pool, smallest-margin-first picks
     whose predicted intent is in the rarest predicted intents (fills tail
     coverage the classifier is weakest on).

Writes (NEW file only):
  evaluation/virgin/al_candidates_300.csv   (300 rows, query_strategy column:
                                             margin/diversity/rare_intent)

Reads (READ-ONLY): data/processed/virgin_inbound_pool.csv, models/intent_virgin.pkl.

Usage:
  .venv\\Scripts\\python.exe scripts\\active_learning.py
"""

import importlib.util
import sys
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
POOL_CSV = ROOT / "data/processed/virgin_inbound_pool.csv"
MODEL = ROOT / "models/intent_virgin.pkl"
OUT = ROOT / "evaluation/virgin/al_candidates_300.csv"

N_MARGIN, N_DIV, N_RARE = 150, 100, 50
SEED = 42


def embedding_backend():
    """MiniLM only if already installed; else TF-IDF. Never installs anything."""
    has_st = importlib.util.find_spec("sentence_transformers") is not None
    has_torch = importlib.util.find_spec("torch") is not None
    return "minilm" if (has_st and has_torch) else "tfidf"


def embed(texts: list, backend: str):
    if backend == "minilm":
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        return model.encode(texts, show_progress_bar=False,
                            convert_to_numpy=True).astype(np.float32)
    from sklearn.feature_extraction.text import TfidfVectorizer
    vec = TfidfVectorizer(sublinear_tf=True, ngram_range=(1, 2),
                          min_df=2, max_features=10000)
    return vec.fit_transform(texts)


def main() -> None:
    if not POOL_CSV.exists():
        raise SystemExit(f"MISSING {POOL_CSV}")
    if not MODEL.exists():
        raise SystemExit(f"MISSING {MODEL}")
    t0 = time.perf_counter()
    rng = np.random.RandomState(SEED)

    pool = pd.read_csv(POOL_CSV, usecols=["tweet_id", "text", "clean"])
    pool["tweet_id"] = pool["tweet_id"].astype("int64")
    texts = pool["text"].fillna("").tolist()
    print(f"pool: {len(pool)} rows")

    bundle = joblib.load(MODEL)
    pipe = bundle["pipeline"] if isinstance(bundle, dict) else bundle
    proba = pipe.predict_proba(texts)
    order = np.argsort(proba, axis=1)
    top1 = proba[np.arange(len(pool)), order[:, -1]]
    top2 = proba[np.arange(len(pool)), order[:, -2]] \
        if proba.shape[1] > 1 else np.zeros(len(pool))
    margin = top1 - top2
    pred = pipe.classes_[order[:, -1]]
    pool["pred_intent"] = pred
    pool["margin"] = margin
    print(f"classifier: {len(pipe.classes_)} intents "
          f"{sorted([str(c) for c in pipe.classes_])}")

    # ---- 1. margin picks: 150 smallest margins ----
    margin_idx = np.argsort(margin, kind="stable")[:N_MARGIN]
    picked = set(int(i) for i in margin_idx)

    # ---- 2. diversity picks: k-means over pool embeddings ----
    backend = embedding_backend()
    print(f"diversity embedding backend: {backend}")
    X = embed(pool["clean"].fillna(pool["text"]).tolist(), backend)
    from sklearn.cluster import KMeans
    km = KMeans(n_clusters=N_DIV, random_state=SEED, n_init=10)
    labels = km.fit_predict(X)
    if hasattr(X, "toarray"):
        Xn = X
        cent = km.cluster_centers_
        # sparse-safe nearest-to-centroid via cosine-ish dot on L2-normalised rows
        from sklearn.preprocessing import normalize as sk_norm
        Xn_n = sk_norm(Xn)
        cent_n = cent / (np.linalg.norm(cent, axis=1, keepdims=True) + 1e-12)
        sim = (Xn_n @ cent_n.T).toarray()
        own_sim = sim[np.arange(len(pool)), labels]
    else:
        Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)
        cent = km.cluster_centers_
        cent_n = cent / (np.linalg.norm(cent, axis=1, keepdims=True) + 1e-12)
        own_sim = np.sum(Xn * cent_n[labels], axis=1)
    div_picks: list = []
    for c in range(N_DIV):
        members = np.where(labels == c)[0]
        members = members[np.argsort(-own_sim[members], kind="stable")]
        for m in members:
            if int(m) not in picked:
                div_picks.append(int(m))
                picked.add(int(m))
                break
    # Shortfall fill (exhausted clusters): smallest margin among remainder.
    if len(div_picks) < N_DIV:
        rest = [i for i in np.argsort(margin, kind="stable")
                if int(i) not in picked]
        for i in rest[:N_DIV - len(div_picks)]:
            div_picks.append(int(i))
            picked.add(int(i))
    assert len(div_picks) == N_DIV, len(div_picks)

    # ---- 3. rare-intent targeted: 50 smallest-margin remainder in rarest intents ----
    counts = pool["pred_intent"].value_counts()
    print("pred intent counts:\n" + counts.to_string())
    rare_order = counts.index.tolist()  # ascending? value_counts is descending
    rare_order = rare_order[::-1]       # rarest first
    remainder = [i for i in np.argsort(margin, kind="stable")
                 if int(i) not in picked]
    rare_set: list = []
    for intent in rare_order:
        if len(rare_set) >= N_RARE:
            break
        for i in remainder:
            if len(rare_set) >= N_RARE:
                break
            if pool.iloc[int(i)]["pred_intent"] == intent and int(i) not in picked:
                rare_set.append(int(i))
                picked.add(int(i))
    # Safety fill (should not trigger): smallest margin among whatever remains.
    if len(rare_set) < N_RARE:
        for i in remainder:
            if len(rare_set) >= N_RARE:
                break
            if int(i) not in picked:
                rare_set.append(int(i))
                picked.add(int(i))
    assert len(rare_set) == N_RARE, len(rare_set)
    print(f"rare-intent order (rarest first): {rare_order}")

    # ---- assemble ----
    rows = []
    for i in margin_idx:
        rows.append((int(i), "margin"))
    for i in div_picks:
        rows.append((int(i), "diversity"))
    for i in rare_set:
        rows.append((int(i), "rare_intent"))
    out = pd.DataFrame({
        "tweet_id": [pool.iloc[i]["tweet_id"] for i, _ in rows],
        "text": [pool.iloc[i]["text"] for i, _ in rows],
        "pred_intent": [pool.iloc[i]["pred_intent"] for i, _ in rows],
        "margin": [round(float(pool.iloc[i]["margin"]), 4) for i, _ in rows],
        "query_strategy": [s for _, s in rows],
    })
    assert len(out) == 300 and out["tweet_id"].nunique() == 300
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)

    print("AL mix:\n" + out["query_strategy"].value_counts().to_string())
    print(f"rare_intent intent mix:\n"
          + out[out.query_strategy == "rare_intent"]["pred_intent"]
          .value_counts().to_string())
    print(f"wrote {OUT} in {time.perf_counter() - t0:.1f}s "
          f"(backend={backend}, seed={SEED})")


if __name__ == "__main__":
    main()
