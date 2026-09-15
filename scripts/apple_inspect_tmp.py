"""AppleSupport subset inspection for TWCS dataset."""
import re, json, sys
import pandas as pd
import numpy as np

RAW = str(Path(__file__).resolve().parents[1] / "data" / "intermediate")
RAW_PATH = str(Path(__file__).resolve().parents[1] / "data" / "raw" / "twcs.csv")
SAMPLE_OUT = str(Path(__file__).resolve().parents[1] / "data" / "intermediate" / "apple_sample.csv")

URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
MENTION_RE = re.compile(r"@\w+")
HASHTAG_RE = re.compile(r"#\w+")
EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F\u200D\u2640-\u2642\u2690-\u2699\u2700-\u27BF\u2B05\u2B06\u2B07\u2B1B\u2B1C\u2B50\u2B55\U0001F004\U0001F0CF]"
)
REPLACEMENT_CHAR = "\ufffd"

print("Scanning raw CSV for AppleSupport subset...", flush=True)
chunks = []
total_rows = 0
for c in pd.read_csv(RAW_PATH, chunksize=200000, low_memory=True, dtype={"author_id": str, "text": str, "response_tweet_id": str, "in_response_to_tweet_id": str, "tweet_id": str, "created_at": str, "inbound": str}):
    total_rows += len(c)
    mask_out = (c["author_id"] == "AppleSupport")
    mask_men = c["text"].str.contains("@AppleSupport", case=False, na=False)
    sub = c[mask_out | mask_men]
    if len(sub):
        chunks.append(sub)
    print(f"  scanned {total_rows}, apple so far {sum(len(x) for x in chunks)}", flush=True)

apple = pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()
print(f"TOTAL raw={total_rows} APPLE union={len(apple)}", flush=True)

# Normalize types
apple["tweet_id_str"] = apple["tweet_id"].astype(str)
# inbound col came as str; normalize to bool
def to_bool(x):
    s = str(x).strip().lower()
    return s == "true"
apple["inbound_bool"] = apple["inbound"].apply(to_bool)

# Analysis sample max 200k
N = len(apple)
if N > 200000:
    ana = apple.sample(n=200000, random_state=42).reset_index(drop=True)
    sampled = True
else:
    ana = apple.reset_index(drop=True)
    sampled = False
print(f"ANALYSIS n={len(ana)} sampled={sampled}", flush=True)

stats = {}
stats["raw_total_rows"] = int(total_rows)
stats["apple_union_rows"] = int(N)
stats["analysis_n"] = int(len(ana))
stats["analysis_sampled_200k"] = bool(sampled)

# inbound/outbound
stats["inbound_true"] = int(ana["inbound_bool"].sum())
stats["inbound_false"] = int((~ana["inbound_bool"]).sum())
stats["author_applesupport_rows"] = int((ana["author_id"] == "AppleSupport").sum())
stats["mention_applesupport_rows"] = int(ana["text"].str.contains("@AppleSupport", case=False, na=False).sum())

# temporal span
dt = pd.to_datetime(ana["created_at"], format="%a %b %d %H:%M:%S %z %Y", errors="coerce")
stats["temporal_parse_fail"] = int(dt.isna().sum())
if dt.notna().any():
    stats["temporal_min"] = str(dt.min())
    stats["temporal_max"] = str(dt.max())
    stats["temporal_span_days"] = float((dt.max() - dt.min()).total_seconds() / 86400.0)
    stats["temporal_month_counts"] = dt.dt.strftime("%Y-%m").value_counts().head(10).to_dict()
else:
    stats["temporal_min"] = None
    stats["temporal_max"] = None
    stats["temporal_span_days"] = None
    stats["temporal_month_counts"] = {}

# text length distribution
txt = ana["text"].fillna("")
char_len = txt.str.len()
word_len = txt.str.split().str.len().fillna(0)
stats["text_char"] = {
    "mean": float(char_len.mean()),
    "median": float(char_len.median()),
    "std": float(char_len.std()),
    "min": int(char_len.min()),
    "max": int(char_len.max()),
    "p25": float(char_len.quantile(0.25)),
    "p75": float(char_len.quantile(0.75)),
    "p90": float(char_len.quantile(0.90)),
    "p95": float(char_len.quantile(0.95)),
}
stats["text_words"] = {
    "mean": float(word_len.mean()),
    "median": float(word_len.median()),
    "std": float(word_len.std()),
    "min": int(word_len.min()),
    "max": int(word_len.max()),
    "p25": float(word_len.quantile(0.25)),
    "p75": float(word_len.quantile(0.75)),
    "p90": float(word_len.quantile(0.90)),
}
# bins
bins = [0, 50, 100, 140, 200, 280, 10000]
hist, _ = np.histogram(char_len, bins=bins)
stats["text_char_hist"] = {f"{bins[i]}-{bins[i+1]}": int(hist[i]) for i in range(len(hist))}

# missing / duplicates
stats["missing"] = {col: int(apple[col].isna().sum()) for col in ["tweet_id", "author_id", "inbound", "created_at", "text", "response_tweet_id", "in_response_to_tweet_id"]}
# empty text
stats["empty_text_rows"] = int((txt.str.strip() == "").sum())
# duplicates
stats["dup_tweet_id"] = int(ana["tweet_id"].duplicated().sum())
stats["dup_text"] = int(txt.duplicated().sum())
stats["dup_rows_full"] = int(ana.duplicated().sum())
# response/in_response missing
def is_missing_resp(x):
    if pd.isna(x):
        return True
    s = str(x).strip().lower()
    return s in ("", "nan", "none", "nat")
stats["response_missing"] = int(ana["response_tweet_id"].apply(is_missing_resp).sum())
stats["in_response_missing"] = int(ana["in_response_to_tweet_id"].apply(is_missing_resp).sum())

# URLs / mentions / hashtags / emoji / noise
has_url = txt.str.contains(URL_RE, na=False)
has_mention = txt.str.contains(MENTION_RE, na=False)
has_hashtag = txt.str.contains(HASHTAG_RE, na=False)
has_emoji = txt.apply(lambda s: bool(EMOJI_RE.search(s)) if isinstance(s, str) else False)
has_nascii = txt.apply(lambda s: any(ord(ch) > 127 for ch in s) if isinstance(s, str) else False)
has_repl = txt.str.contains(REPLACEMENT_CHAR, na=False)
stats["pct_url"] = float(has_url.mean())
stats["n_url"] = int(has_url.sum())
stats["pct_mention"] = float(has_mention.mean())
stats["pct_hashtag"] = float(has_hashtag.mean())
stats["n_hashtag"] = int(has_hashtag.sum())
stats["pct_emoji"] = float(has_emoji.mean())
stats["n_emoji"] = int(has_emoji.sum())
stats["pct_nascii"] = float(has_nascii.mean())
stats["n_nascii"] = int(has_nascii.sum())
stats["pct_replacement_char"] = float(has_repl.mean())
stats["n_replacement_char"] = int(has_repl.sum())
# avg mentions per tweet
avg_mentions = txt.apply(lambda s: len(MENTION_RE.findall(s)) if isinstance(s, str) else 0)
stats["avg_mentions_per_tweet"] = float(avg_mentions.mean())
# top mentions (cap to avoid emoji print issues; ascii only)
all_mentions = []
for s in txt.head(200000):
    if isinstance(s, str):
        all_mentions.extend([m.lower() for m in MENTION_RE.findall(s)])
from collections import Counter
mc = Counter(all_mentions)
stats["top_mentions"] = {k: int(v) for k, v in mc.most_common(10)}
# top hashtags ascii-safe
all_tags = []
for s in txt:
    if isinstance(s, str):
        all_tags.extend([m.lower() for m in HASHTAG_RE.findall(s)])
stats["top_hashtags"] = {k: int(v) for k, v in Counter(all_tags).most_common(10)}
stats["n_unique_hashtags"] = int(len(set(all_tags)))

# Language noise heuristics (no langdetect lib): non-ascii sample + simple non-English token markers
spanish_markers = ["gracias", "hola", "por favor", "ayuda", "mi iphone", "que "]
# count rows containing common Spanish/French/Dutch markers as proxy
def contains_any(s, words):
    sl = s.lower()
    return any(w in sl for w in words)
french_markers = ["merci", "bonjour", "s'il", "mon iphone"]
dutch_markers = ["dank je", "hallo", "mijn iphone"]
stats["heuristic_spanish_like"] = int(txt.apply(lambda s: contains_any(s, spanish_markers) if isinstance(s, str) else False).sum())
stats["heuristic_french_like"] = int(txt.apply(lambda s: contains_any(s, french_markers) if isinstance(s, str) else False).sum())
stats["heuristic_dutch_like"] = int(txt.apply(lambda s: contains_any(s, dutch_markers) if isinstance(s, str) else False).sum())
# non-latin script heuristic
stats["n_nonlatin_sample"] = 0
nonlatin_re = re.compile(r"[\u0400-\u04FF\u0600-\u06FF\u4E00-\u9FFF\uAC00-\uD7AF\u0E00-\u0E7F]")
stats["pct_nonlatin"] = float(txt.apply(lambda s: bool(nonlatin_re.search(s)) if isinstance(s, str) else False).mean())

# Thread reconstruction via union-find on analysis sample
parent = {}
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        parent[rb] = ra

ids = ana["tweet_id"].astype(str).tolist()
idset = set(ids)
for i in ids:
    parent[i] = i

def parse_ids(v):
    if pd.isna(v):
        return []
    s = str(v).strip()
    if s.lower() in ("", "nan", "none", "nat"):
        return []
    parts = re.split(r"[,;\s]+", s)
    out = []
    for p in parts:
        p = p.strip()
        # keep numeric-like (may be '123.0')
        try:
            if "." in p:
                p = str(int(float(p)))
            else:
                p = str(int(p))
            out.append(p)
        except Exception:
            continue
    return out

dangling_response = 0
total_response_links = 0
dangling_inresp = 0
total_inresp_links = 0
multi_response_rows = 0
for idx, row in ana.iterrows():
    tid = str(row["tweet_id"])
    # normalize tid to int-string
    try:
        tid_norm = str(int(float(tid)))
    except Exception:
        tid_norm = tid
    for rid in parse_ids(row["response_tweet_id"]):
        total_response_links += 1
        if rid in idset:
            union(tid_norm if tid_norm in parent else tid, rid)
        else:
            dangling_response += 1
    rlist = parse_ids(row["response_tweet_id"])
    if len(rlist) > 1:
        multi_response_rows += 1
    for rid in parse_ids(row["in_response_to_tweet_id"]):
        total_inresp_links += 1
        if rid in idset:
            union(tid_norm if tid_norm in parent else tid, rid)
        else:
            dangling_inresp += 1

# fix: parent keys are original ids; normalize mapping by rebuilding with normalized keys
# Recompute components sizes
from collections import Counter as C
roots = C()
for i in ids:
    try:
        k = str(int(float(i)))
        if k not in parent:
            # fallback to original
            k = i
    except Exception:
        k = i
    # find root handling missing normalized keys
    key = i if i in parent else k
    roots[find(key)] += 1
sizes = list(roots.values())
stats["threads_n"] = int(len(sizes))
if sizes:
    import numpy as np2
    arr = np2.array(sizes)
    stats["thread_size"] = {
        "mean": float(arr.mean()),
        "median": float(np2.median(arr)),
        "max": int(arr.max()),
        "min": int(arr.min()),
    }
    stats["thread_size_dist"] = {
        "1": int((arr == 1).sum()),
        "2": int((arr == 2).sum()),
        "3-5": int(((arr >= 3) & (arr <= 5)).sum()),
        "6-10": int(((arr >= 6) & (arr <= 10)).sum()),
        "11+": int((arr >= 11).sum()),
    }
    stats["pct_singleton_threads"] = float((arr == 1).sum() / len(arr))
else:
    stats["thread_size"] = {}
    stats["thread_size_dist"] = {}
    stats["pct_singleton_threads"] = 0.0
stats["total_response_links"] = int(total_response_links)
stats["dangling_response_links"] = int(dangling_response)
stats["total_inresp_links"] = int(total_inresp_links)
stats["dangling_inresp_links"] = int(dangling_inresp)
stats["multi_response_rows"] = int(multi_response_rows)

# Inbound/outbound per thread approx: skip detailed, give overall alternation proxy
# outbound text prefix stats: % starting with @mention
outbound = ana[~ana["inbound_bool"]]
inbound = ana[ana["inbound_bool"]]
stats["outbound_start_with_mention_pct"] = float(outbound["text"].fillna("").str.strip().str.startswith("@").mean()) if len(outbound) else 0.0
stats["inbound_start_with_mention_pct"] = float(inbound["text"].fillna("").str.strip().str.startswith("@").mean()) if len(inbound) else 0.0

print("STATS_JSON_START")
print(json.dumps(stats, indent=2, ensure_ascii=True))
print("STATS_JSON_END")

# Save 5000-row sample (from full apple, random, seed 42)
samp = apple.sample(n=min(5000, len(apple)), random_state=42).reset_index(drop=True)
# keep original column order (drop helper cols)
drop_cols = [c for c in ["tweet_id_str", "inbound_bool"] if c in samp.columns]
samp = samp.drop(columns=drop_cols)
samp.to_csv(SAMPLE_OUT, index=False, encoding="utf-8")
print(f"Saved sample {len(samp)} -> {SAMPLE_OUT}", flush=True)
