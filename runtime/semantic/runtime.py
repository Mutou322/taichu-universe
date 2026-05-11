"""语义运行时 — 语义层的 API 桥接

职责：
- 编译 wiki → SemanticNode
- 构建图谱 → GraphData
- 提供统一的 build_graph / search / related 接口
- 不直接操作 storage 层
"""

from pathlib import Path
from typing import Optional

import sys
sys.path.insert(0, str(Path.home() / "taichu" / "config"))
sys.path.insert(0, str(Path.home() / "taichu"))
from paths import paths

from knowledge.graph.builder import GraphBuilder
from knowledge.relations.relation import RelationType


class SemanticRuntime:
    """语义运行时 API — Layer 2 的对外接口"""

    def __init__(self):
        self.builder = GraphBuilder()
        self._graph_cache = None

    # ── 图谱构建 ──

    def build_graph(self) -> dict:
        """构建完整语义图谱，返回 {nodes: [SemanticNode], edges: [SemanticRelation]}"""
        wiki_dir = paths.wiki_dir
        self._graph_cache = self.builder.build(str(wiki_dir))
        return self._graph_cache

    def _ensure_graph(self):
        if self._graph_cache is None:
            return self.build_graph()
        return self._graph_cache

    # ── 查询 API ──

    def search(self, query: str, limit: int = 20) -> list[dict]:
        """按名称搜索节点（模糊匹配）"""
        graph = self._ensure_graph()
        q = query.lower()
        results = []
        for node in graph["nodes"]:
            if q in node.title.lower() or q in node.summary.lower():
                results.append(node)
        return results[:limit]

    def related(self, node_id: str) -> list[dict]:
        """获取某个节点的关联节点"""
        graph = self._ensure_graph()
        related_ids = set()

        for edge in graph["edges"]:
            if edge.source == node_id:
                related_ids.add(edge.target)
            if edge.target == node_id:
                related_ids.add(edge.source)

        node_map = {n.id: n for n in graph["nodes"]}
        results = []
        for rid in related_ids:
            if rid in node_map:
                results.append(node_map[rid])
            else:
                results.append({
                    "id": rid,
                    "title": rid,
                    "summary": "(被引用)",
                    "links": [],
                })
        return results

    # ── 属性 ──

    @property
    def node_count(self) -> int:
        return len(self._ensure_graph()["nodes"])

    @property
    def edge_count(self) -> int:
        return len(self._ensure_graph()["edges"])

    def refresh(self):
        """强制重建图谱"""
        self._graph_cache = None
        return self.build_graph()


# 单例
semantic = SemanticRuntime()
