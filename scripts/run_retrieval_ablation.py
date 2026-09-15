"""Retrieval ablation runner (workstream A2, docs/WIN_PLAN.md).

Calls the SHIPPED endpoint POST /eval/retrieval-ablation (in-process
TestClient, default body: k=[1,5] x arms=[keyword, virgin_nn] x
context=[0,2] on the fixed 60-item golden_human_200 seed-7 slice) and writes
evaluation/virgin/RETRIEVAL_ABLATION.md FROM the endpoint response, so the
docs table matches endpoint output by construction.

Reproduce: C:\\Hiver\\.venv\\Scripts\\python.exe C:\\Hiver\\scripts\\run_retrieval_ablation.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Hiver")

VIRGIN_DIR = Path(r"C:\Hiver\evaluation\virgin")
OUT_MD = VIRGIN_DIR / "RETRIEVAL_ABLATION.md"


def main():
    from fastapi.testclient import TestClient
    import backend.main as app_mod

    c = TestClient(app_mod.app)
    resp = c.post("/eval/retrieval-ablation", json={})
    assert resp.status_code == 200, resp.text[:300]
    obj = resp.json()
    arms = obj["arms"]
    assert len(arms) == 8, f"expected 8 arms, got {len(arms)}"
    for a in arms:
        for k in ("name", "recall_proxy", "groundedness_mean", "groundedness_ge4_rate",
                  "p50_ms", "p95_ms", "support_rate", "context_hit_rate", "n"):
            assert k in a, f"arm {a.get('name')} missing {k}"

    print(f"brand={obj['brand']} n={obj['n']} slice={obj['slice']} entailment={obj['entailment']}")
    for a in arms:
        print(f"  {a['name']:22s} recall={a['recall_proxy']:.3f} ground={a['groundedness_mean']:.2f} "
              f"ge4={a['groundedness_ge4_rate']:.3f} support={a['support_rate']:.3f} "
              f"ctx_hit={a['context_hit_rate']:.3f} p50={a['p50_ms']:.1f}ms p95={a['p95_ms']:.1f}ms")

    head = ("| arm | recall_proxy | ground_mean | ground>=4 | support_rate | "
            "ctx_hit | p50_ms | p95_ms |")
    sep = "|---|---|---|---|---|---|---|---|"
    body = [f"| {a['name']} | {a['recall_proxy']:.3f} | {a['groundedness_mean']:.2f} | "
            f"{a['groundedness_ge4_rate']:.3f} | {a['support_rate']:.3f} | "
            f"{a['context_hit_rate']:.3f} | {a['p50_ms']:.1f} | {a['p95_ms']:.1f} |"
            for a in arms]
    # Headline deltas (fixed pairs, read off the table, not hand-picked).
    by = {a["name"]: a for a in arms}

    def _d(key, a, b):
        return round(by[b][key] - by[a][key], 3)

    lines = [
        "# Virgin retrieval ablation (workstream A2)",
        "",
        f"- Slice: `{obj['slice']}` (fixed 60 rows of golden_human_200, seed 7; read-only, no data files mutated).",
        "- Fixed: classifier + templates (final LogReg); only retrieval varies: depth k=1 vs 5, "
        "retriever keyword (BM25 over virgin KB) vs virgin_nn (TF-IDF-NN), thread context 0 vs 2 prior turns.",
        "- Metrics per arm: recall_proxy (lexical token-F1>=0.15 hit — disclosed PROXY, no relevance labels exist), "
        "groundedness_mean + >=4 rate (frozen heuristic, same estimator as BASELINE_VS_FINAL.md), "
        "support_rate (claim-entailment of the template draft vs arm passages — the retrieval-sensitive signal), "
        "context_hit_rate (share where thread context was found), retrieval p50/p95 ms.",
        "- Entailment: heuristic-offline (deterministic; reproduces without a Groq key).",
        "- Source of truth: `POST /eval/retrieval-ablation` (this table is rendered from a live endpoint response).",
        "",
        head, sep, *body,
        "",
        "## Reading",
        f"- Depth k=1->5 (virgin_nn, ctx=0): recall_proxy "
        f"{by['virgin_nn:k=1:ctx=0']['recall_proxy']:.3f}->{by['virgin_nn:k=5:ctx=0']['recall_proxy']:.3f} "
        f"(delta {_d('recall_proxy', 'virgin_nn:k=1:ctx=0', 'virgin_nn:k=5:ctx=0'):+.3f}), "
        f"support_rate {by['virgin_nn:k=1:ctx=0']['support_rate']:.3f}->"
        f"{by['virgin_nn:k=5:ctx=0']['support_rate']:.3f} "
        f"(delta {_d('support_rate', 'virgin_nn:k=1:ctx=0', 'virgin_nn:k=5:ctx=0'):+.3f}).",
        f"- Retriever keyword->virgin_nn (k=5, ctx=0): recall_proxy "
        f"{by['keyword:k=5:ctx=0']['recall_proxy']:.3f}->{by['virgin_nn:k=5:ctx=0']['recall_proxy']:.3f} "
        f"(delta {_d('recall_proxy', 'keyword:k=5:ctx=0', 'virgin_nn:k=5:ctx=0'):+.3f}), "
        f"support_rate {by['keyword:k=5:ctx=0']['support_rate']:.3f}->"
        f"{by['virgin_nn:k=5:ctx=0']['support_rate']:.3f} "
        f"(delta {_d('support_rate', 'keyword:k=5:ctx=0', 'virgin_nn:k=5:ctx=0'):+.3f}).",
        f"- Context 0->2 (virgin_nn, k=5): support_rate "
        f"{by['virgin_nn:k=5:ctx=0']['support_rate']:.3f}->"
        f"{by['virgin_nn:k=5:ctx=2']['support_rate']:.3f} "
        f"(delta {_d('support_rate', 'virgin_nn:k=5:ctx=0', 'virgin_nn:k=5:ctx=2'):+.3f}); "
        f"context_hit_rate={by['virgin_nn:k=5:ctx=2']['context_hit_rate']:.3f} "
        "(exact/normalized thread-parquet match; misses fall back to the raw query, so the arm mixes context value with query-robustness).",
        "- Groundedness-heuristic columns barely move across arms BY DESIGN: the frozen heuristic scores template "
        "shape (DM + 'Check' + length + cite), and every arm retrieves >=1 passage, so it saturates. "
        "That is the circularity BASELINE_VS_FINAL.md discloses — the retrieval-sensitive evidence is support_rate, not ground_mean.",
        "- Latency: all arms p50/p95 in low ms (CPU-only, in-process); BM25 over 27k KB docs is the slowest leg.",
        "",
        "## What is misleading (mandatory)",
        "- recall_proxy is lexical overlap, not judged relevance: k=5 dominates k=1 mechanically (max over a bigger set). Read it as coverage, not quality.",
        "- support_rate inherits the V3 strict-instrument caveat (JUDGE_AGREEMENT_V3.md): absolute levels are low everywhere; ARM DIFFERENCES are the signal, not absolutes.",
        "- n=60 single-annotator slice: arm deltas have wide CIs; this reframes the +0.005 intent story toward retrieval, it does not replace a judged study.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
