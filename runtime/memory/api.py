"""记忆运行时 API — 统一的知识库读写入口，底层委托 storage 层"""

import logging
from typing import Optional

from paths import paths

logger = logging.getLogger(__name__)

# ── 指标记录常量 ──
METRIC_QUERY_PREVIEW_LENGTH = 50


class MemoryRuntime:
    """统一记忆运行时 API"""

    def __init__(self) -> None:
        self._store = None
        self._embedder = None
        self.wiki_dir = paths.wiki_dir
        self.chroma_dir = paths.chroma_dir

    # ── 延迟初始化 ──

    def _get_store(self):
        if self._store is None:
            from storage.vector.chroma_store import ChromaStore

            self._store = ChromaStore(str(self.chroma_dir))
        return self._store

    def _get_embedder(self):
        if self._embedder is None:
            from storage.embeddings.embedder import Embedder

            self._embedder = Embedder()
        return self._embedder

    # ── 语义搜索 ──

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        """语义搜索知识库，返回 [{title, score, text}, ...]"""
        # 加 trace
        from runtime.metrics.collector import metrics_collector
        from runtime.metrics.counters import metrics_counters
        from runtime.metrics.retrieval_latency import RetrievalMetrics
        from runtime.metrics.timers import metric_timer
        from runtime.metrics.tracing import runtime_tracer

        trace = runtime_tracer.start("retrieval_pipeline")

        # 嵌入阶段
        with metric_timer("embedding", query=query[:30]):
            embedder = self._get_embedder()
            q_emb = embedder.embed(query)

        # 搜索阶段
        with metric_timer("vector_search", query=query[:30]):
            store = self._get_store()
            results = None
            for col in ["kb_articles", "evomind", "taichu_memory"]:
                try:
                    results = store.query_by_embedding(q_emb, limit=top_k, collection=col)
                    if results.get("ids") and results["ids"][0]:
                        break
                except Exception as e:
                    logger.debug("search query over collection %s failed: %s", col, e)
                    continue

        metrics_counters.increment("searches")

        if results is None or not results["ids"] or not results["ids"][0]:
            runtime_tracer.finish(trace)
            metrics_counters.increment("empty_results")
            return []

        items = []
        for i in range(len(results["ids"][0])):
            meta = results["metadatas"][0][i] if results["metadatas"] else {}
            items.append(
                {
                    "title": meta.get("source", results["ids"][0][i]),
                    "score": 1.0 / (1.0 + results["distances"][0][i]) if results["distances"] else 0.0,
                    "text": results["documents"][0][i] if results["documents"] else "",
                }
            )

        runtime_tracer.finish(trace)
        metrics_counters.increment("results_found", len(items))

        # 记录检索指标
        metrics_collector.record_retrieval(
            RetrievalMetrics(
                query=query[:METRIC_QUERY_PREVIEW_LENGTH],
                total_ms=trace.duration_ms(),
                result_count=len(items),
            )
        )

        return items

    # ── 存储 ──

    def store(self, doc_id: str, text: str, metadata: Optional[dict] = None) -> bool:
        """存入一条知识到 ChromaDB"""
        try:
            store = self._get_store()
            store.add(doc_id, text, metadata or {})

            return True
        except Exception as e:
            logger.warning("store 失败: %s", e)
            return False

    # ── 嵌入 ──

    def embed(self, text: str) -> list[float]:
        return self._get_embedder().embed(text)

    # ── 删除 ──

    def delete(self, doc_id: str) -> bool:
        try:
            self._get_store().delete(doc_id)

            return True
        except Exception as e:
            logger.warning("delete 失败: %s", e)
            return False

    # ── 统计 ──

    @property
    def count(self) -> int:
        try:
            return self._get_store().count
        except Exception as e:
            logger.warning("count failed: %s", e)
            return 0


# 单例（由 runtime.bootstrap 统一管理，此处仅作导入兼容）
from runtime.bootstrap import get_memory as _get_memory

memory = _get_memory()
