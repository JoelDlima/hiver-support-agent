"""TF-IDF NearestNeighbors retriever over AppleSupport replies. Reuses data/indexes."""
from pathlib import Path
import joblib
import pandas as pd

INDEX_DIR = Path(r"C:\Hiver\data\indexes")
KB_PATH = Path(r"C:\Hiver\data\processed\apple_kb.csv")

class Retriever:
    def __init__(self):
        self.vec = joblib.load(INDEX_DIR / "tfidf_vectorizer.pkl")
        self.nn = joblib.load(INDEX_DIR / "nn_index.pkl")
        ids = pd.read_csv(INDEX_DIR / "doc_ids.csv")
        self.doc_ids = ids["tweet_id"].astype(str).tolist()
        # Load raw texts for display (lazy: from KB if available else from raw)
        if KB_PATH.exists():
            kb = pd.read_csv(KB_PATH, usecols=["tweet_id", "text", "clean"])
            self.lookup = {str(r.tweet_id): (r.text, r.clean) for r in kb.itertuples()}
        else:
            self.lookup = {}

    def query(self, text: str, k: int = 5):
        Xq = self.vec.transform([text.lower()])
        dist, idx = self.nn.kneighbors(Xq, n_neighbors=min(k, len(self.doc_ids)))
        out = []
        for d, j in zip(dist[0], idx[0]):
            tid = self.doc_ids[j]
            raw, clean = self.lookup.get(tid, ("", ""))
            out.append({"tweet_id": tid, "distance": float(d), "score": float(1 - d), "text": raw, "clean": clean})
        return out
