"""
runtime/retrieval/rerank.py — 检索结果二次排序

支持 graph-aware rerank，兼容统一的 graph_centrality 字段。
"""

from typing import Dict, List

from runtime.metrics.timers import metric_timer


def rerank_docs(docs: List[Dict], query: str = "") -> List[Dict]:
    """
    Cross-encoder / graph-aware rerank。

    排序权重: final_score(0.6) + graph_centrality(0.4)
    """
    if not docs:
        return docs

    # 统一字段名
    from runtime.schema import normalize_retrieval_doc

    for doc in docs:
        normalize_retrieval_doc(doc)

    with metric_timer("rerank", query=query[:30]):
        for doc in docs:
            doc["rerank_score"] = 0.6 * doc.get("final_score", 0.5) + 0.4 * doc.get("graph_centrality", 0.5)

        docs.sort(key=lambda x: x["rerank_score"], reverse=True)

    return docs
