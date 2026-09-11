# SearXNG research runbook (Hiver expedition, local instance)

Endpoint: `http://127.0.0.1:8888/search?q=<query>&format=json&language=en`
Status (2026-09-12): LIVE, verified 26 results across duckduckgo + google-cse on test query.
Docs: https://docs.searxng.org/ (user syntax, configured engines, search API).

## Start (fresh PowerShell)
```powershell
$env:SEARXNG_SETTINGS_PATH="C:\Hiver\searxng\hiver-settings.yml"
$env:PYTHONPATH="C:\Hiver\searxng\winshim"   # pwd stub, Windows-only, never called
Start-Process -FilePath "C:\Hiver\searxng\.venv-sxng\Scripts\python.exe" `
  -ArgumentList "-m","searx.webapp" -WorkingDirectory "C:\Hiver\searxng" `
  -WindowStyle Hidden -RedirectStandardOutput "C:\Hiver\searxng\sxng-out.log" `
  -RedirectStandardError "C:\Hiver\searxng\sxng-err.log"
```

## Query (JSON API — https://docs.searxng.org/dev/search_api.html)
```powershell
# PowerShell smoke test
Invoke-RestMethod "http://127.0.0.1:8888/search?q=SetFit+few-shot&format=json&language=en" |
  Select-Object -ExpandProperty results | Select-Object engine,title,url -First 10
```
```python
# Python (agents): multi-engine fetch + URL dedup
import json, urllib.request, urllib.parse
def sxng(q, n=12):
    qs = urllib.parse.urlencode({"q": q, "format": "json", "language": "en"})
    req = urllib.request.Request("http://127.0.0.1:8888/search?" + qs,
                                 headers={"User-Agent": "hiver-research/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.load(r)
    seen, out = set(), []
    for x in d.get("results", []):
        u = x.get("url") or ""
        if u and u not in seen:
            seen.add(u); out.append((x.get("engine"), x.get("title"), u))
        if len(out) >= n: break
    return out
```

## Rules for research agents
1. SearXNG FIRST for every question (multi-engine: ddg, wikipedia, arxiv,
   semantic_scholar, openalex, crossref, stackexchange, hackernews, mojeek,
   marginalia, mwmbl, github). Record query + engines that returned hits.
2. Then webfetch top 2–4 PRIMARY sources (papers, official docs/repos).
3. Session websearch only as fallback when SearXNG is thin (note it in the ledger).
4. Pace queries ~3–5s apart; engines rate-limit residential IPs.
5. Known quirks: `disabled:true` overrides for underscore-named engines
   (google_cse, bing_news, …) do not apply — they run anyway (bonus coverage).
   No limiter.toml warning is expected (limiter disabled). Flask dev server only.

## Stop
```powershell
Get-Process python -ErrorAction SilentlyContinue |
  Where-Object { $_.Path -like "*searxng*" } | Stop-Process -Force
```

## Footprint
Clone 25.6 MB + venv ~80 MB + logs. https://docs.searxng.org/admin/installation.html
documents docker/script/step-by-step installs; this instance uses the Flask dev
server path (no Docker on this machine, granian is Linux-only).
