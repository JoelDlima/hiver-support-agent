"""Single DDG fetch with Firefox UA. Usage: ddg_one.py <query> <track>"""
import sys, re, random, html as H
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
from pathlib import Path
from datetime import datetime
query, track = sys.argv[1], sys.argv[2]
FIREFOX_UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
]
TAG_RE = re.compile(r"<[^>]+>")
A_RE = re.compile(r'<a[^>]+class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.S)
LITE_RE = re.compile(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', re.S)
def clean(s):
    return H.unescape(TAG_RE.sub("", s or "")).strip()[:220]
status, res = "challenged_or_error", []
for base in ["https://lite.duckduckgo.com/lite/?q=", "https://duckduckgo.com/html/?q="]:
    try:
        req = Request(base + quote_plus(query), headers={"User-Agent": random.choice(FIREFOX_UAS)})
        with urlopen(req, timeout=25) as r:
            html = r.read().decode("utf-8", errors="ignore")
        if "challenge" in html.lower() and len(html) < 9000:
            continue
        m = A_RE.findall(html) or LITE_RE.findall(html)
        out = []
        for href, title in m:
            t = clean(title)
            if not t or "duckduckgo" in href.lower() or len(t) < 15:
                continue
            out.append((t, href[:180]))
            if len(out) >= 4:
                break
        if out:
            status, res = "ok-firefoxUA", out
            break
    except Exception:
        continue
ts = datetime.now().strftime("%H:%M:%S")
finding = ("; ".join(t for t, _ in res[:2])[:280]) if res else "DDG challenge/empty — no invented finding"
with open(        Path(__file__).resolve().parents[1] / "docs" / "research" / "mixed_18min_log.md", "a", encoding="utf-8") as f:
    f.write(f"\n## {ts} [ddg-firefoxUA:{status}] {query}\n")
    for t, h in res[:4]:
        f.write(f"- {t} — {h}\n")
    if not res:
        f.write("- (blocked; fallback to normal search later)\n")
with open(Path(__file__).resolve().parents[1] / "docs" / "research_log.md", "a", encoding="utf-8") as f:
    f.write(f"- DATE: 2026-09-10 / QUERY: {query} / SOURCE: DuckDuckGo FirefoxUA ({status}) / KEY FINDING: {finding} / RELEVANCE: {track} / IMPACT: mixed-18min session\n")
print(f"[{ts}] ddg-firefox {status} n={len(res)} :: {query[:60]}")
