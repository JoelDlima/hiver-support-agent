"""Graphify repo-graph artifact regression (offline-built, Graphify-Labs/graphify).

Asserts the committed graphify-out/ artifact stays structurally valid and fresh:
- graph.json loads, node/link counts above build floor (1017/1737 at build)
- required schema fields present (id/label/file_type/source_file)
- key system nodes present (agent core + docs overlay)
- doc overlay edges resolve to real nodes (no dangling documents edges)
- freshness: manifest commit recorded; warns (not fails) when HEAD moved on
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GDIR = ROOT / "graphify-out"
GRAPH = GDIR / "graph.json"

VALID_FILE_TYPES = {"code", "document", "paper", "image", "rationale", "concept"}


def _load():
    g = json.loads(GRAPH.read_text(encoding="utf-8"))
    return g


def test_artifact_files_exist():
    assert GRAPH.exists(), "graph.json missing — rebuild: python -m graphify . --out graphify-out --code-only"
    assert (GDIR / "graph.html").exists()
    assert (GDIR / "GRAPH_REPORT.md").exists()
    assert (GDIR / "docs_overlay.json").exists()


def test_graph_scale_floor():
    g = _load()
    assert len(g["nodes"]) >= 1000, len(g["nodes"])
    assert len(g["links"]) >= 1700, len(g["links"])


def test_schema_fields():
    g = _load()
    for n in g["nodes"]:
        for f in ("id", "label", "file_type", "source_file"):
            assert f in n, (f, n.get("id"))
        assert n["file_type"] in VALID_FILE_TYPES, n["file_type"]
    ids = {n["id"] for n in g["nodes"]}
    for e in g["links"]:
        for f in ("source", "target", "relation", "confidence", "source_file"):
            assert f in e, f
        assert e["source"] in ids, e["source"]
        assert e["target"] in ids, e["target"]


def _ids_ending(suffix: str) -> list:
    g = _load()
    return [n["id"] for n in g["nodes"] if n["id"].endswith(suffix)]


def test_key_system_nodes_present():
    # merge-graphs namespaces ids (Hiver:: / Hiver-2::) — match by suffix.
    for must in ("src_agent_appleagent", "src_agent",
                 "src_groq_draft_draft_with_groq", "src_review_store",
                 "doc:readme", "doc:report_virgin_6page"):
        assert _ids_ending(must), must


def test_docs_overlay_edges_resolve():
    g = _load()
    doc_edges = [e for e in g["links"] if e.get("_origin") == "docs-overlay"]
    assert len(doc_edges) >= 50, len(doc_edges)
    assert any(e["relation"] == "documents" for e in doc_edges)


def test_freshness_logged():
    r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT)
    head = (r.stdout or "").strip()
    report = (GDIR / "GRAPH_REPORT.md").read_text(encoding="utf-8")
    assert "Built from commit" in report
    # informational only: print staleness for the log, never fail on it
    print(f"\ngraph built at commit in report; HEAD now {head[:8]}")
