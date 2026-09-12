"""Build VirginTrains KB manifest (Phase 1b, item 1.7).

READ-ONLY over existing CSVs (never modifies build_virgin_kb.py outputs).
Reads:  data/processed/virgin_kb.csv (+ data/indexes/virgin/doc_ids.csv for a
        consistency count only).
Writes: evaluation/virgin/kb_manifest.json with:
  - content_sha256 per row (sha256 of the raw `text` field, utf-8, as-is)
  - corpus fingerprint (sha256 over sorted per-row hashes)
  - counts, params (all heuristic definitions), git_sha
Prints a 5-number quality card:
  exact-dup rate | near-dup estimate | boilerplate share |
  non-English share | URL rate

Heuristic definitions (also stored in the manifest `params`):
- exact-dup: 1 - nunique(content_sha256) / n_rows
- near-dup: same over near_hash = sha256(normalized text) where normalized =
  lowercase, URLs removed, @handles removed, non-alphanumeric stripped,
  whitespace collapsed. An estimate (independent of any clustering).
- boilerplate: share of rows matching >=1 BOILERPLATE_RES (case-insensitive).
- non-English: share of rows with >=1 alphabetic char where <50% of
  alphabetic chars are ASCII a-z (ASCII-ratio heuristic, no language model).
- URL: share of rows containing http:// or https://.

Usage: PYTHONPATH=C:\\Hiver C:\\Hiver\\.venv\\Scripts\\python.exe C:\\Hiver\\scripts\\build_virgin_manifest.py
"""

import csv
import datetime as _dt
import hashlib
import json
import re
import subprocess
from pathlib import Path

KB = Path(r"C:\Hiver\data\processed\virgin_kb.csv")
DOC_IDS = Path(r"C:\Hiver\data\indexes\virgin\doc_ids.csv")
OUT = Path(r"C:\Hiver\evaluation\virgin\kb_manifest.json")

URL_RE = re.compile(r"https?://\S+")
HANDLE_RE = re.compile(r"@\w+")
NONALNUM_RE = re.compile(r"[^a-z0-9\s]")
WS_RE = re.compile(r"\s+")

BOILERPLATE_RES = [
    r"contact us on our website",
    r"please\s+dm\b",
    r"\bdm us\b",
    r"aftersales team",
    r"0344\s*556\s*5650",
    r"sorry for (any|the)",
    r"thanks for getting in touch",
    r"please contact us",
]
BOILERPLATE_COMPILED = [re.compile(p, re.IGNORECASE) for p in BOILERPLATE_RES]


def content_hash(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def near_normalize(text: str) -> str:
    t = (text or "").lower()
    t = URL_RE.sub(" ", t)
    t = HANDLE_RE.sub(" ", t)
    t = NONALNUM_RE.sub(" ", t)
    return WS_RE.sub(" ", t).strip()


def near_hash(text: str) -> str:
    return hashlib.sha256(near_normalize(text).encode("utf-8")).hexdigest()


def is_boilerplate(text: str) -> bool:
    return any(rx.search(text or "") for rx in BOILERPLATE_COMPILED)


def is_non_english(text: str) -> bool:
    letters = [c for c in (text or "") if c.isalpha()]
    if not letters:
        return False
    ascii_letters = sum(1 for c in letters if "a" <= c.lower() <= "z")
    return (ascii_letters / len(letters)) < 0.5


def has_url(text: str) -> bool:
    t = text or ""
    return "http://" in t or "https://" in t


def git_sha() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                             text=True, timeout=15, cwd=str(KB.parents[2]))
        sha = (out.stdout or "").strip()
        return sha if sha else "unknown"
    except Exception:
        return "unknown"


def main() -> None:
    if not KB.exists():
        raise SystemExit(f"MISSING {KB} — run V-DATA scripts/build_virgin_kb.py first.")

    rows = []
    with open(KB, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames or []
        if "text" not in columns:
            raise SystemExit(f"{KB} has no 'text' column (cols={columns})")
        id_col = "tweet_id" if "tweet_id" in columns else columns[0]
        for i, row in enumerate(reader):
            tid = row.get(id_col, "")
            text = row.get("text", "") or ""
            rows.append({"row": i, "tweet_id": str(tid),
                         "content_sha256": content_hash(text)})

    n = len(rows)
    texts = []
    with open(KB, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            texts.append(row.get("text", "") or "")

    exact_hashes = [r["content_sha256"] for r in rows]
    near_hashes = [near_hash(t) for t in texts]
    n_exact_unique = len(set(exact_hashes))
    n_near_unique = len(set(near_hashes))
    n_boiler = sum(1 for t in texts if is_boilerplate(t))
    n_non_en = sum(1 for t in texts if is_non_english(t))
    n_url = sum(1 for t in texts if has_url(t))

    quality = {
        "exact_dup_rate": round(1 - n_exact_unique / n, 4) if n else 0.0,
        "near_dup_rate_estimate": round(1 - n_near_unique / n, 4) if n else 0.0,
        "boilerplate_share": round(n_boiler / n, 4) if n else 0.0,
        "non_english_share": round(n_non_en / n, 4) if n else 0.0,
        "url_rate": round(n_url / n, 4) if n else 0.0,
    }

    doc_ids_count = None
    if DOC_IDS.exists():
        with open(DOC_IDS, encoding="utf-8", newline="") as f:
            doc_ids_count = sum(1 for _ in f) - 1  # minus header

    manifest = {
        "kb_path": "data/processed/virgin_kb.csv",
        "n_rows": n,
        "columns": columns,
        "rows": rows,
        "corpus_fingerprint_sha256": hashlib.sha256(
            "\n".join(sorted(exact_hashes)).encode("utf-8")).hexdigest(),
        "counts": {
            "n_rows": n,
            "n_unique_exact": n_exact_unique,
            "n_unique_near": n_near_unique,
            "n_boilerplate": n_boiler,
            "n_non_english": n_non_en,
            "n_url": n_url,
            "doc_ids_count": doc_ids_count,
        },
        "quality": quality,
        "params": {
            "content_sha256": "sha256 hex of raw `text` field, utf-8, as-is",
            "corpus_fingerprint": "sha256 over newline-joined sorted per-row hashes",
            "near_normalize": "lowercase; strip URLs/@handles; drop non-[a-z0-9\\s]; collapse whitespace",
            "boilerplate_patterns": BOILERPLATE_RES,
            "non_english_rule": "rows with >=1 alpha char where ascii(a-z)/alpha < 0.5",
            "url_rule": "raw text contains 'http://' or 'https://'",
        },
        "git_sha": git_sha(),
        "built_at_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("== Virgin KB quality card (5 numbers) ==")
    print(f"exact-dup rate:      {quality['exact_dup_rate']:.4f}")
    print(f"near-dup estimate:   {quality['near_dup_rate_estimate']:.4f}")
    print(f"boilerplate share:   {quality['boilerplate_share']:.4f}")
    print(f"non-English share:   {quality['non_english_share']:.4f}")
    print(f"URL rate:            {quality['url_rate']:.4f}")
    print(f"n_rows={n} fingerprint={manifest['corpus_fingerprint_sha256'][:16]}… "
          f"git_sha={manifest['git_sha'][:12] if len(manifest['git_sha']) > 12 else manifest['git_sha']}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
