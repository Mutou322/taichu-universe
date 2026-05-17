"""
runtime/retrieval/rerank.py — 检索结果二次排序

支持 graph-aware rerank，兼容统一的 graph_centrality 字段。
"""

from runtime.metrics.timers import metric_timer

# ── Rerank 权重 ──
RERANK_FINAL_SCORE_WEIGHT = 0.6
RERANK_GRAPH_CENTRALITY_WEIGHT = 0.4
RERANK_DEFAULT_SCORE = 0.5


def rerank_docs(docs: list[dict], query: str = "") -> list[dict]:
    """
    Cross-encoder / graph-aware rerank。

    排序权重: final_score(RERANK_FINAL_SCORE_WEIGHT) + graph_centrality(RERANK_GRAPH_CENTRALITY_WEIGHT)
    """
    if not docs:
        return docs

    # 统一字段名
    from runtime.schema import normalize_retrieval_doc

    for doc in docs:
        normalize_retrieval_doc(doc)

    with metric_timer("rerank", query=query[:30]):
        for doc in docs:
            doc["rerank_score"] = RERANK_FINAL_SCORE_WEIGHT * doc.get(
                "final_score", RERANK_DEFAULT_SCORE
            ) + RERANK_GRAPH_CENTRALITY_WEIGHT * doc.get("graph_centrality", RERANK_DEFAULT_SCORE)

        docs.sort(key=lambda x: x["rerank_score"], reverse=True)

    return docs
