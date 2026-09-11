"""Mine safety/money slice from virgin pool for powered recall reporting.
Rulebook-assisted labels (documented); reports system recall on safety + money separately.
Writes evaluation/virgin/safety_slice.csv + prints recall.
"""
import re
import pandas as pd
from pathlib import Path
from src.agent import AppleAgent

POOL = Path(r"C:\Hiver\data\processed\virgin_inbound_pool.csv")
OUT = Path(r"C:\Hiver\evaluation\virgin\safety_slice.csv")
SAFETY_RE = re.compile(r"flame|burn|fire|smoke|injur|stranded|evacuat|stampede|derail|packed|rammed|crush|overcrowd", re.I)
MONEY_RE = re.compile(r"refund|repay|compensation|chargeback|charged|overcharg|£|\$", re.I)

def main(n_cap=60, seed=9):
    df = pd.read_csv(POOL, usecols=["text"]).dropna().drop_duplicates()
    saf = df[df.text.str.contains(SAFETY_RE, na=False)]
    mon = df[df.text.str.contains(MONEY_RE, na=False)]
    take_s = saf.sample(min(20, len(saf)), random_state=seed)
    take_m = mon.sample(min(40, len(mon)), random_state=seed)
    sl = pd.concat([take_s.assign(slice="safety"), take_m.assign(slice="money")]).drop_duplicates("text").reset_index(drop=True)
    try:
        from backend.main import get_agent
        agent = get_agent("virgin")
    except Exception:
        from src.retriever import Retriever
        try:
            retr = Retriever()
        except Exception:
            retr = None
        agent = AppleAgent(retr, brand="virgin")
    rows = []
    for t in sl.text.tolist():
        o = agent.handle(t, "virgin")
        rows.append({"text": t, "slice": "", "pred_esc": 1 if o.decision == "escalate" else 0,
                     "pred_reason": o.escalate_reason, "intent": o.intent})
    res = pd.DataFrame(rows)
    res["slice"] = list(sl["slice"]) if len(sl) == len(res) else ""
    # Expected: safety slice should ALL escalate; money slice should mostly escalate
    for s in ["safety", "money"]:
        sub = res[res.slice == s]
        if len(sub):
            print(f"{s}: n={len(sub)} recall={sub.pred_esc.mean():.3f}")
    res.to_csv(OUT, index=False)
    print(f"wrote {len(res)} -> {OUT}")

if __name__ == "__main__":
    main()
