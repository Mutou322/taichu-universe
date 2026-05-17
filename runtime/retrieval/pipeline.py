"""检索管线 — Phase 2 全链路检索：解析→向量搜索→图谱扩展→过滤→重排序→构建上下文"""

import asyncio

from runtime.metrics.metrics_bus import metrics_bus
from runtime.metrics.models import MetricEvent
from runtime.metrics.timers import metric_timer
from runtime.metrics.tracing import runtime_tracer
from runtime.retrieval.context_builder import build_context
from runtime.retrieval.graph_expand import expand_graph
from runtime.retrieval.ontology_filter import filter_by_ontology
from runtime.retrieval.query_parser import parse_query
from runtime.retrieval.rerank import rerank_docs
from runtime.retrieval.vector_search import hybrid_vector_search


async def run_retrieval_pipeline(query: str) -> tuple[str, list[dict]]:
    """
    Phase 2 全链路 Retrieval Pipeline
    带 Phase 1 Metrics
    """
    trace_root = runtime_tracer.start("retrieval_pipeline")
    docs = []
    context = ""

    # Step 1: query_parser
    with metric_timer("query_parser", query=query):
        trace_parser = runtime_tracer.start("query_parser")
        qd = parse_query(query)
        runtime_tracer.finish(trace_parser)

    # Step 2: hybrid_vector_search
    with metric_timer("vector_search", query=qd.get("topic", query)[:30]):
        trace_vector = runtime_tracer.start("vector_search")
        docs = hybrid_vector_search(qd, top_k=20)
        runtime_tracer.finish(trace_vector)

    # Step 3: graph_expand
    with metric_timer("graph_expand"):
        trace_graph = runtime_tracer.start("graph_expand")
        docs = expand_graph(docs, max_depth=2, max_neighbors=5)
        runtime_tracer.finish(trace_graph)

    # Step 4: ontology_filter
    with metric_timer("ontology_filter"):
        trace_ontology = runtime_tracer.start("ontology_filter")
        docs = filter_by_ontology(docs, allowed_categories=None)  # None = 不过滤，等 GBrain ontology 稳定后启用
        runtime_tracer.finish(trace_ontology)

    # Step 5: rerank
    with metric_timer("rerank"):
        trace_rerank = runtime_tracer.start("rerank")
        docs = rerank_docs(docs, query=query)
        runtime_tracer.finish(trace_rerank)

    # Step 6: context_builder
    with metric_timer("context_builder"):
        trace_context = runtime_tracer.start("context_builder")
        context = build_context(docs)
        runtime_tracer.finish(trace_context)

    # emit pipeline metrics
    event = MetricEvent(name="retrieval_pipeline_completed", value=len(docs), tags={"query": query[:30]})
    try:
        asyncio.create_task(metrics_bus.emit_async(event.name, event))
    except RuntimeError:
        pass

    runtime_tracer.finish(trace_root)

    return context, docs
