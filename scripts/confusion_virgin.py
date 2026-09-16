"""Virgin confusion matrix: human_intent x pred_intent from judge_scores_200.csv.

Writes evaluation/virgin/confusion_human200.csv (rows = human label,
cols = predicted label, counts; last column = row total n).
Prints intent accuracy, Cohen's kappa, and the top-5 confusions.

Usage: PYTHONPATH=. .venv\\Scripts\\python.exe scripts\\confusion_virgin.py
"""

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.virgin_intents import INTENTS  # noqa: E402

VIRGIN_DIR = ROOT / "evaluation" / "virgin"
SRC = VIRGIN_DIR / "judge_scores_200.csv"
DST = VIRGIN_DIR / "confusion_human200.csv"


def main():
    import pandas as pd
    from sklearn.metrics import accuracy_score, cohen_kappa_score

    df = pd.read_csv(SRC)
    yt = df["human_intent"].tolist()
    yp = df["pred_intent"].tolist()
    labels = list(INTENTS) + sorted((set(yt) | set(yp)) - set(INTENTS))
    counts = Counter(zip(yt, yp))

    with open(DST, "w", newline="", encoding="utf-8") as f:
        f.write("human_intent\\pred_intent," + ",".join(labels) + ",n\n")
        for a in labels:
            row = [str(counts.get((a, p), 0)) for p in labels]
            f.write(a + "," + ",".join(row) + "," + str(sum(counts.get((a, p), 0) for p in labels)) + "\n")

    acc = accuracy_score(yt, yp)
    kap = cohen_kappa_score(yt, yp)
    print("wrote %s (n=%d)" % (DST, len(df)))
    print("intent_acc=%.3f kappa=%.3f" % (acc, kap))
    print("top-5 confusions (human -> pred : n):")
    shown = 0
    for (a, p), c in counts.most_common():
        if a != p:
            print("  %s -> %s : %d" % (a, p, c))
            shown += 1
            if shown >= 5:
                break


if __name__ == "__main__":
    main()
