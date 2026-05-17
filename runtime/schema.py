"""
太初知识宇宙 — Schema 统一定义

所有模块通过此模块访问统一的数据类型和接口定义，
避免字段名不一致（如 graph_score vs graph_centrality）和模块缺失崩溃。
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════
# 图谱 Schema
# ═══════════════════════════════════════════


class SemanticNode:
    """语义图谱节点"""

    def __init__(
        self,
        id: str,
        label: str = "",
        summary: str = "",
        content: str = "",
        links: Optional[list] = None,
        gravity: float = 1.0,
        cluster_id: int = 0,
    ):
        self.id = id
        self.title = label or id
        self.label = label or id
        self.summary = summary
        self.content = content
        self.links = links or []
        self.gravity = gravity
        self.cluster_id = cluster_id


class SemanticRelation:
    """语义图谱边（关系）"""

    def __init__(self, source: str, target: str, weight: float = 1.0, relation_type: str = "related"):
        self.source = source
        self.target = target
        self.from_id = source
        self.to_id = target
        self.weight = weight
        self.relation_type = relation_type


def make_graph_data(nodes: list, edges: list) -> dict:
    """统一的图谱数据结构"""
    return {
        "nodes": nodes,
        "edges": edges,
        "total_nodes": len(nodes),
    }


# ═══════════════════════════════════════════
# 检索 Schema
# ═══════════════════════════════════════════

# 统一检索结果字段名（替代分散的 graph_score / graph_centrality）
RETRIEVAL_SCORE_FIELDS = {
    "vector_score": "vector_score",
    "graph_score": "graph_centrality",  # 统一为 graph_centrality
    "recency_score": "recency_score",
    "ontology_score": "ontology_score",
    "final_score": "final_score",
    "rerank_score": "rerank_score",
}


def normalize_retrieval_doc(doc: dict) -> dict:
    """统一检索文档字段名"""
    mapping = {
        "graph_score": "graph_centrality",
    }
    for old_key, new_key in mapping.items():
        if old_key in doc and new_key not in doc:
            doc[new_key] = doc[old_key]
    return doc


# ═══════════════════════════════════════════
# MemoryRuntime 接口协议（用于降级）
# ═══════════════════════════════════════════


class MemoryProtocol:
    """MemoryRuntime 接口协议，所有实现必须提供这些方法"""

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        raise NotImplementedError

    def store(self, doc_id: str, text: str, metadata: dict | None = None) -> bool:
        raise NotImplementedError

    def delete(self, doc_id: str) -> bool:
        raise NotImplementedError

    @property
    def count(self) -> int:
        raise NotImplementedError


# ═══════════════════════════════════════════
# 事件 Schema
# ═══════════════════════════════════════════


class MetricEvent:
    """指标事件"""

    def __init__(self, name: str, value: float = 0.0, tags: Optional[dict] = None):
        self.name = name
        self.value = value
        self.tags = tags or {}


# ═══════════════════════════════════════════
# 可选依赖安全导入
# ═══════════════════════════════════════════


def safe_import(module_name: str, fallback: Any = None) -> Any:
    """
    安全导入模块，失败时返回 fallback 而非崩溃。
    用于依赖可选的外部库（如 ChromaDB、sentence-transformers）。
    """
    try:
        import importlib

        return importlib.import_module(module_name)
    except ImportError:
        return fallback
    except Exception as e:
        logger.debug("safe_import(%s) failed: %s", module_name, e)
        return fallback
