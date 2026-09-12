"""Re-attach docs-overlay `documents` edges after graphify merge-graphs.

merge-graphs namespaces each input graph (Hiver:: / Hiver-2::), which orphans
cross-graph edges authored against unprefixed ids (they are dropped). This script
resolves each doc->file mention from docs_links.json against the merged graph's
actual node ids (tries `Hiver::<fid>`, then bare `<fid>`) and appends the edge
with _origin=docs-overlay. Deterministic; evidence = literal path mentions.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GDIR = ROOT / "graphify-out"
GRAPH = GDIR / "graph.json"
LINKS = GDIR / "docs_links.json"


def file_node_id(rel: str) -> str:
    # graphify file-node ids drop the extension: src/agent.py -> src_agent
    stem = str(Path(rel).with_suffix(""))
    return re.sub(r"[^a-z0-9]+", "_", stem.lower()).strip("_")


def main():
    g = json.loads(GRAPH.read_text(encoding="utf-8"))
    ids = {n["id"] for n in g["nodes"]}
    pairs = json.loads(LINKS.read_text(encoding="utf-8"))

    def doc_id(dslug: str) -> str | None:
        for cand in (f"Hiver-2::{dslug}", dslug):
            if cand in ids:
                return cand
        hits = [i for i in ids if i.endswith(dslug)]
        return hits[0] if hits else None

    have = {(e["source"], e["target"], e["relation"]) for e in g["links"]}
    added, skipped = 0, []
    for dslug, files in pairs.items():
        src = doc_id(dslug)
        if src is None:
            skipped.append((dslug, "<doc-missing>"))
            continue
        for rel in files:
            tgt = None
            for cand in (f"Hiver::{file_node_id(rel)}", file_node_id(rel)):
                if cand in ids:
                    tgt = cand
                    break
            if tgt is None:
                skipped.append((dslug, rel))
                continue
            key = (src, tgt, "documents")
            if key in have:
                continue
            have.add(key)
            g["links"].append({"source": src, "target": tgt, "relation": "documents",
                               "confidence": "EXTRACTED", "confidence_score": 1.0,
                               "source_file": rel, "_origin": "docs-overlay", "weight": 1.0})
            added += 1
    GRAPH.write_text(json.dumps(g, indent=1), encoding="utf-8")
    print(f"repaired: +{added} documents edges, skipped {len(skipped)}")
    for s in skipped[:10]:
        print("  skip:", s)


if __name__ == "__main__":
    main()
