"""Deterministic docs overlay for the Graphify code graph (no LLM, no key).

Scans curated project docs, emits graphify-schema nodes/edges:
- document node per doc (id `doc:<slug>`, file_type `document`)
- section nodes for `##` headings (`doc:<slug>#<sec>`, relation `contains`)
- `documents` edges from doc to code file-nodes for literal backticked/bare
  repo-path mentions that resolve to real nodes in graph.json (EXTRACTED).

Merge: `python -m graphify merge-graphs graphify-out/graph.json
graphify-out/docs_overlay.json --out graphify-out/graph_merged.json`
then re-run cluster-only + export html. Honesty: structural extraction only
(headings + literal path mentions), never semantic claims.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRAPH = ROOT / "graphify-out" / "graph.json"
OUT = ROOT / "graphify-out" / "docs_overlay.json"

DOCS = [
    "README.md",
    "docs/REPORT_VIRGIN_6PAGE.md",
    "docs/DECISION_LOG.md",
    "docs/UNIQUENESS.md",
    "docs/ANNOTATION_PROTOCOL.md",
    "evaluation/virgin/BASELINE_VS_FINAL.md",
    "evaluation/virgin/JUDGE_AGREEMENT.md",
    "evaluation/virgin/LLM_JUDGE_30.md",
    "evaluation/virgin/SAMPLING_NOTE.md",
    "evaluation/virgin/FAILURE_TESTS.md",
    "research/expedition/LEDGER.md",
    "research/expedition/LEDGER_WAVE2.md",
    "research/expedition/PLAN_V2.md",
    "autonomy_matrix.yaml",
    "promptfooconfig.yaml",
    "graphify-out/GRAPH_REPORT.md",
]

PATH_RE = re.compile(r"`((?:src|scripts|backend|evaluation|models|frontend-next|tests|docs|research|eval_providers)/[A-Za-z0-9_./-]+)`")
BARE_RE = re.compile(r"(?<![\w/`])((?:src|scripts|backend|evaluation|models|tests)/[A-Za-z0-9_./-]+\.(?:py|md|csv|json|yaml|yml))")
HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")


def slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s[:64] or "section"


def file_node_id(rel: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", rel.lower()).strip("_")


def main():
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    node_ids = {n["id"] for n in graph["nodes"]}
    nodes, links = [], []
    for rel in DOCS:
        p = ROOT / rel
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        dslug = slug(Path(rel).stem)
        did = f"doc:{dslug}"
        title = rel
        for line in text.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()[:100]
                break
        nodes.append({"id": did, "label": title, "file_type": "document",
                      "source_file": rel})
        seen_sec = set()
        for line in text.splitlines():
            m = HEADING_RE.match(line)
            if m:
                sec = slug(m.group(1))
                if sec not in seen_sec:
                    seen_sec.add(sec)
                    sid = f"{did}#{sec}"
                    nodes.append({"id": sid, "label": m.group(1).strip()[:80],
                                  "file_type": "document", "source_file": rel})
                    links.append({"source": did, "target": sid, "relation": "contains",
                                  "confidence": "EXTRACTED", "confidence_score": 1.0,
                                  "source_file": rel, "_origin": "docs-overlay", "weight": 1.0})
        targets = set(PATH_RE.findall(text)) | set(BARE_RE.findall(text))
        for t in sorted(targets):
            fid = file_node_id(t)
            if fid in node_ids:
                links.append({"source": did, "target": fid, "relation": "documents",
                              "confidence": "EXTRACTED", "confidence_score": 1.0,
                              "source_file": rel, "_origin": "docs-overlay", "weight": 1.0})
    # dedup
    seen_n, unodes = set(), []
    for n in nodes:
        if n["id"] not in seen_n:
            seen_n.add(n["id"])
            unodes.append(n)
    seen_e, ulinks = set(), []
    for e in links:
        k = (e["source"], e["target"], e["relation"])
        if k not in seen_e:
            seen_e.add(k)
            ulinks.append(e)
    OUT.write_text(json.dumps({"directed": True, "multigraph": False, "graph": {},
                               "nodes": unodes, "links": ulinks, "hyperedges": []},
                              indent=1), encoding="utf-8")
    print(f"overlay: {len(unodes)} nodes, {len(ulinks)} edges -> {OUT}")
    # Doc→file mention pairs for post-merge repair (merge-graphs namespaces each
    # input graph, so cross-graph `documents` edges dangle and are dropped — the
    # repair step re-attaches them to the namespaced file nodes).
    pairs = {}
    for rel in DOCS:
        p = ROOT / rel
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        dslug = slug(Path(rel).stem)
        did = f"doc:{dslug}"
        targets = set(PATH_RE.findall(text)) | set(BARE_RE.findall(text))
        pairs[did] = sorted(t for t in targets if (ROOT / t).exists())
    pairs_path = ROOT / "graphify-out" / "docs_links.json"
    pairs_path.write_text(json.dumps(pairs, indent=1), encoding="utf-8")
    print(f"pairs: {sum(len(v) for v in pairs.values())} doc->file mentions -> {pairs_path}")


if __name__ == "__main__":
    main()
