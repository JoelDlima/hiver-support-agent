"""Build VirginTrains TF-IDF + NearestNeighbors index (Phase 1 V-MODEL).

Reads:  C:\\Hiver\\data\\processed\\virgin_kb.csv  (created by V-DATA scripts/build_virgin_kb.py)
Writes: C:\\Hiver\\data\\indexes\\virgin\\{tfidf_vectorizer.pkl,nn_index.pkl,doc_ids.csv,tfidf_matrix.npz,index_meta.json}

Fail-closed: if virgin_kb.csv missing, exits with clear message (V-DATA not done yet).
Usage: PYTHONPATH=C:\\Hiver C:\\Hiver\\.venv\\Scripts\\python.exe C:\\Hiver\\scripts\\build_virgin_index.py
"""
import csv
import json
import re
import time
from pathlib import Path

import joblib
import numpy as np

KB = Path(r"C:\Hiver\data\processed\virgin_kb.csv")
OUT = Path(r"C:\Hiver\data\indexes\virgin")
OUT.mkdir(parents=True, exist_ok=True)

URL_RE = re.compile(r"https?://\S+")
HANDLE_RE = re.compile(r"@\w+")


def clean(text: str) -> str:
    text = URL_RE.sub(" url ", text or "")
    text = HANDLE_RE.sub(" user ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def main() -> None:
    if not KB.exists():
        print(f"MISSING {KB} — run V-DATA scripts/build_virgin_kb.py first (or follow-up).")
        print(f"Ensured empty index dir exists: {OUT}")
        # Write placeholder meta so downstream checks know index is pending
        meta = {"brand": "virgin", "status": "pending", "reason": "virgin_kb.csv missing", "n_docs": 0}
        (OUT / "index_meta.json").write_text(json.dumps(meta, indent=2))
        return
    from scipy import sparse
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.neighbors import NearestNeighbors

    t0 = time.perf_counter()
    ids, texts = [], []
    # virgin_kb.csv expected cols: tweet_id,text[,clean]; fallback to text-only
    import pandas as pd
    try:
        df = pd.read_csv(KB)
        id_col = "tweet_id" if "tweet_id" in df.columns else df.columns[0]
        txt_col = "text" if "text" in df.columns else df.columns[1] if len(df.columns) > 1 else df.columns[0]
        for _, row in df.iterrows():
            c = clean(str(row[txt_col] or ""))
            if c:
                ids.append(str(row[id_col]))
                texts.append(c)
    except Exception:
        with open(KB, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                tid = row.get("tweet_id") or row.get("id") or ""
                c = clean(row.get("text", ""))
                if c and tid:
                    ids.append(str(tid))
                    texts.append(c)
    t_load = time.perf_counter() - t0
    print(f"loaded {len(texts)} Virgin replies in {t_load:.1f}s from {KB}")
    if not texts:
        print("empty KB — nothing to index")
        return

    t1 = time.perf_counter()
    vec = TfidfVectorizer(sublinear_tf=True, ngram_range=(1, 2),
                          min_df=2, max_features=50000, stop_words="english")
    X = vec.fit_transform(texts)
    nn = NearestNeighbors(n_neighbors=5, metric="cosine", algorithm="brute")
    nn.fit(X)
    t_build = time.perf_counter() - t1
    print(f"TF-IDF {X.shape} fit + NN index in {t_build:.1f}s")

    probes = ["train delayed claim delay repay", "change advance ticket refund",
              "platform timetable disruption", "lost bag on train"] * 5
    lat = []
    for q in probes:
        s = time.perf_counter()
        nn.kneighbors(vec.transform([q]))
        lat.append((time.perf_counter() - s) * 1000)
    lat = np.array(lat)
    print(f"query latency ms: p50={np.median(lat):.1f} p95={np.percentile(lat, 95):.1f}")

    joblib.dump(vec, OUT / "tfidf_vectorizer.pkl")
    sparse.save_npz(OUT / "tfidf_matrix.npz", X)
    joblib.dump(nn, OUT / "nn_index.pkl")
    with open(OUT / "doc_ids.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["row", "tweet_id"])
        w.writerows(enumerate(ids))
    meta = {"brand": "virgin", "status": "ready", "n_docs": len(texts), "matrix_shape": list(X.shape),
            "load_s": round(t_load, 1), "build_s": round(t_build, 1),
            "latency_ms_p50": round(float(np.median(lat)), 1),
            "latency_ms_p95": round(float(np.percentile(lat, 95)), 1),
            "total_s": round(time.perf_counter() - t0, 1)}
    (OUT / "index_meta.json").write_text(json.dumps(meta, indent=2))
    print("meta:", json.dumps(meta))


if __name__ == "__main__":
    main()
