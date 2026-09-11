"""Train intent classifier on weak labels from inbound pool."""
import pandas as pd
from pathlib import Path
from src import classifier as clf_mod

POOL = Path(r"C:\Hiver\data\processed\apple_inbound_pool.csv")

def main(n=30000, seed=42):
    df = pd.read_csv(POOL, usecols=["text"]).dropna().sample(min(n, 9999999), random_state=seed)
    # weak labels
    labels = [clf_mod.weak_label(t) for t in df.text.tolist()]
    df["weak"] = labels
    print(df.weak.value_counts().to_string())
    pipe = clf_mod.train(df.text.tolist(), labels)
    print(f"trained -> {clf_mod.MODEL_PATH}, classes={pipe.classes_.tolist()}")
    # quick train-acc sanity
    from sklearn.metrics import accuracy_score
    pred = pipe.predict(df.text.tolist()[:2000])
    print("train-subset acc (vs weak, optimistic):", round(accuracy_score(labels[:2000], pred), 3))

if __name__ == "__main__":
    main()
