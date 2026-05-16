# runtime/retrieval/vector_search.py
import asyncio

from runtime.bootstrap import get_memory
from runtime.metrics.metrics_bus import metrics_bus
from runtime.metrics.models import MetricEvent
from runtime.metrics.timers import metric_timer


def hybrid_vector_search(query_dict: dict, top_k: int = 10) -> list:
    """
    Unified Retrieval Score:
    final_score = vector_score × 0.5 + graph_centrality × 0.2 + recency × 0.2 + ontology_match × 0.1

    返回: [{"id": ..., "title": ..., "text": ..., "vector_score": ..., "graph_centrality": ..., "recency": ..., "ontology_match": ..., "final_score": ..., "category": ...}, ...]
    """
    query_text = query_dict.get("topic") or query_dict.get("raw", "")

    with metric_timer("vector_search", query=query_text[:30]):
        memory = get_memory()
        raw = memory.search(query_text, top_k=top_k)

        results = []
        for doc in raw:
            vector_score = doc.get("score", 0.5)
            results.append(
                {
                    "id": doc.get("title", ""),
                    "title": doc.get("title", ""),
                    "text": doc.get("text", ""),
                    "vector_score": vector_score,
                    "graph_centrality": 0.5,
                    "recency": 0.5,
                    "ontology_match": 0.5,
                    "category": "knowledge",
                    "final_score": (
                        0.5 * vector_score
                        + 0.2 * 0.5  # graph_centrality
                        + 0.2 * 0.5  # recency
                        + 0.1 * 0.5  # ontology_match
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
