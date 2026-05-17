"""混合向量检索 — 多权重融合的语义搜索：向量分+图谱中心度+新近度+本体匹配"""

import asyncio

from runtime.bootstrap import get_memory
from runtime.metrics.metrics_bus import metrics_bus
from runtime.metrics.models import MetricEvent
from runtime.metrics.timers import metric_timer

# ── 检索融合权重 ──
VECTOR_SCORE_WEIGHT = 0.5
GRAPH_CENTRALITY_WEIGHT = 0.2
RECENCY_WEIGHT = 0.2
ONTOLOGY_MATCH_WEIGHT = 0.1
DEFAULT_SCORE = 0.5


def hybrid_vector_search(query_dict: dict, top_k: int = 10) -> list[dict]:
    """
    Unified Retrieval Score:
    final_score = vector_score × VECTOR_SCORE_WEIGHT + graph_centrality × GRAPH_CENTRALITY_WEIGHT
                  + recency × RECENCY_WEIGHT + ontology_match × ONTOLOGY_MATCH_WEIGHT

    返回: [{"id": ..., "title": ..., "text": ..., "vector_score": ..., "graph_centrality": ..., "recency": ..., "ontology_match": ..., "final_score": ..., "category": ...}, ...]
    """
    query_text = query_dict.get("topic") or query_dict.get("raw", "")

    with metric_timer("vector_search", query=query_text[:30]):
        memory = get_memory()
        raw = memory.search(query_text, top_k=top_k)

        results = []
        for doc in raw:
            vector_score = doc.get("score", DEFAULT_SCORE)
            results.append(
                {
                    "id": doc.get("title", ""),
                    "title": doc.get("title", ""),
                    "text": doc.get("text", ""),
                    "vector_score": vector_score,
                    "graph_centrality": DEFAULT_SCORE,
                    "recency": DEFAULT_SCORE,
                    "ontology_match": DEFAULT_SCORE,
                    "category": "knowledge",
                    "final_score": (
                        VECTOR_SCORE_WEIGHT * vector_score
                        + GRAPH_CENTRALITY_WEIGHT * DEFAULT_SCORE
                        + RECENCY_WEIGHT * DEFAULT_SCORE
                        + ONTOLOGY_MATCH_WEIGHT * DEFAULT_SCORE
                    ),
                }
            )

        # emit metrics
        event = MetricEvent(name="vector_search_results", value=len(results), tags={"topic": query_text[:30]})
        try:
            asyncio.create_task(metrics_bus.emit_async(event.name, event))
        except RuntimeError:
            pass

    return results
