"""Baseline retrieval repro: TF-IDF + sklearn NearestNeighbors over AppleSupport replies.

CPU-only, stdlib + pandas + scikit-learn + scipy (already in .venv).
Persists artifacts to C:\\Hiver\\data\\indexes for reuse by downstream agents.
Usage: C:\\Hiver\\.venv\\Scripts\\python.exe C:\\Hiver\\scripts\\build_retrieval_baseline.py
"""
import csv
import json
import re
import time
from pathlib import Path

import joblib
import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "twcs.csv"
OUT = ROOT / "data" / "indexes"
OUT.mkdir(parents=True, exist_ok=True)

URL_RE = re.compile(r"https?://\S+")
HANDLE_RE = re.compile(r"@\w+")


def clean(text: str) -> str:
    text = URL_RE.sub(" url ", text or "")
    text = HANDLE_RE.sub(" user ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def main() -> None:
    t0 = time.perf_counter()
    ids, texts = [], []
    with open(RAW, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            # Grounded reply corpus: outbound AppleSupport tweets only
            if row.get("author_id") == "AppleSupport" and row.get("inbound") == "False":
                c = clean(row.get("text", ""))
                if c:
                    ids.append(row["tweet_id"])
                    texts.append(c)
    t_load = time.perf_counter() - t0
    print(f"loaded {len(texts)} AppleSupport replies in {t_load:.1f}s")

    t1 = time.perf_counter()
    vec = TfidfVectorizer(sublinear_tf=True, ngram_range=(1, 2),
                          min_df=2, max_features=50000, stop_words="english")
    X = vec.fit_transform(texts)
    nn = NearestNeighbors(n_neighbors=5, metric="cosine", algorithm="brute")
    nn.fit(X)
    t_build = time.perf_counter() - t1
    print(f"TF-IDF {X.shape} fit + NN index in {t_build:.1f}s")

    # Latency probe: 20 representative support queries
    probes = ["iphone battery drains fast", "forgot apple id password reset",
              "ios update failed error", "macbook screen flickering",
              "airpods not connecting bluetooth"] * 4
    lat = []
    for q in probes:
        s = time.perf_counter()
        nn.kneighbors(vec.transform([q]))
        lat.append((time.perf_counter() - s) * 1000)
    lat = np.array(lat)
    print(f"query latency ms: p50={np.median(lat):.1f} p95={np.percentile(lat, 95):.1f}")

    # Persist
    joblib.dump(vec, OUT / "tfidf_vectorizer.pkl")
    sparse.save_npz(OUT / "tfidf_matrix.npz", X)
    joblib.dump(nn, OUT / "nn_index.pkl")
    with open(OUT / "doc_ids.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["row", "tweet_id"])
        w.writerows(enumerate(ids))
    meta = {"n_docs": len(texts), "matrix_shape": list(X.shape),
            "load_s": round(t_load, 1), "build_s": round(t_build, 1),
            "latency_ms_p50": round(float(np.median(lat)), 1),
            "latency_ms_p95": round(float(np.percentile(lat, 95)), 1),
            "total_s": round(time.perf_counter() - t0, 1)}
    (OUT / "index_meta.json").write_text(json.dumps(meta, indent=2))
    print("meta:", json.dumps(meta))

    # Demo: top-5 with tweet_id citations for one query
    d, idx = nn.kneighbors(vec.transform(["my iphone battery dies quickly after ios update"]))
    print("demo query top-5 (dist, tweet_id):")
    for dist, j in zip(d[0], idx[0]):
        print(f"  {dist:.3f}  {ids[j]}  {texts[j][:100]}")


if __name__ == "__main__":
    main()
