"""Train VirginTrains intent classifier on weak labels from virgin inbound pool.

Mirrors scripts/train_classifier.py (Apple) for brand=virgin:
- weak-label virgin_inbound_pool (<=30k) via src.virgin_intents KEYWORDS
  (first-match, support_access_followup last — same rule as agent._weak_label_generic)
- TF-IDF (1,2)-gram LogReg, same hyperparams as src/classifier.build_pipeline
- output models/intent_virgin.pkl (per brands.py virgin.model_path)

Usage: PYTHONPATH=C:\\Hiver C:\\Hiver\\.venv\\Scripts\\python.exe C:\\Hiver\\scripts\\train_virgin.py
"""
import joblib
import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from src.text_norm import normalize
from src.virgin_intents import INTENTS, KEYWORDS
from src.agent import _weak_label_generic

POOL = Path(r"C:\Hiver\data\processed\virgin_inbound_pool.csv")
MODEL_PATH = Path(r"C:\Hiver\models\intent_virgin.pkl")


def build_pipeline() -> Pipeline:
    vec = TfidfVectorizer(preprocessor=normalize, lowercase=False,
                          ngram_range=(1, 2), min_df=3, max_features=30000, sublinear_tf=True)
    # balanced: accessibility has 167/30000 weak hits; without weights the LogReg
    # buries the tail (accessibility F1 0.500 pre-fix). Revisit with human labels >500.
    clf = LogisticRegression(max_iter=1000, C=2.0, class_weight="balanced")
    return Pipeline([("tfidf", vec), ("clf", clf)])


def main(n=30000, seed=42):
    df = pd.read_csv(POOL, usecols=["text"]).dropna()
    df = df.sample(min(n, len(df)), random_state=seed).reset_index(drop=True)
    labels = [_weak_label_generic(t, KEYWORDS) for t in df.text.tolist()]
    df["weak"] = labels
    print(f"pool_sample={len(df)} (seed {seed}, cap {n})")
    print(df.weak.value_counts().to_string())
    pipe = build_pipeline()
    pipe.fit(df.text.tolist(), labels)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": pipe, "labels": INTENTS}, MODEL_PATH)
    print(f"trained -> {MODEL_PATH}, classes={pipe.classes_.tolist()}")
    from sklearn.metrics import accuracy_score
    pred = pipe.predict(df.text.tolist()[:2000])
    print("train-subset acc (vs weak, optimistic):", round(accuracy_score(labels[:2000], pred), 3))


if __name__ == "__main__":
    main()
