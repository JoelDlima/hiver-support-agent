import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support
from src.agent import AppleAgent, trivial_baseline, keyword_baseline
from src.retriever import Retriever
df = pd.read_csv(r"C:\Hiver\evaluation\golden_human_60.csv")
yt = df.human_intent.tolist(); ye = df.human_escalate.astype(int).tolist()
retr = Retriever(); agent = AppleAgent(retr)
rows = []
for name, fn in [('trivial', trivial_baseline), ('simple-keyword', lambda t: keyword_baseline(t, retr)), ('final', agent.handle)]:
    outs = [fn(t) for t in df.text.tolist()]
    pi = [o.intent for o in outs]; pe = [1 if o.decision == 'escalate' else 0 for o in outs]
    acc = accuracy_score(yt, pi); macro = f1_score(yt, pi, average='macro', zero_division=0)
    p, r, f, _ = precision_recall_fscore_support(ye, pe, average='binary', zero_division=0)
    rows.append((name, round(acc, 3), round(macro, 3), round(float(p), 3), round(float(r), 3), round(float(f), 3)))
    print(name, rows[-1][1:])
pd.DataFrame(rows, columns=['system', 'intent_acc', 'macroF1', 'esc_P', 'esc_R', 'esc_F1']).to_csv(r"C:\Hiver\evaluation\results_human60.csv", index=False)
