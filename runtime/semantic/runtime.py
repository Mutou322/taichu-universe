"""语义运行时 — 语义层的 API 桥接

职责：
- 编译 wiki → SemanticNode
- 构建图谱 → GraphData（含邻接索引）
- 提供统一的 build_graph / search / related 接口
- 不直接操作 storage 层
"""

from collections import defaultdict

from paths import paths

from knowledge.graph.builder import GraphBuilder


class SemanticRuntime:
    """语义运行时 API — Layer 2 的对外接口"""

    def __init__(self) -> None:
        self.builder = GraphBuilder()
        self._graph_cache = None
        self._adjacency: dict[str, set[str]] = {}
        self._weight_map: dict[tuple[str, str], float] = {}

    # ── 图谱构建 ──

    def _build_adjacency(self):
        """从 edges 重建邻接索引 + 权重索引（O(e) 构建，后续 O(1) 查询）"""
        adj: dict[str, set[str]] = defaultdict(set)
        wmap: dict[tuple[str, str], float] = {}
        if self._graph_cache is None:
            return
        for edge in self._graph_cache["edges"]:
            adj[edge.source].add(edge.target)
            adj[edge.target].add(edge.source)
            wmap[(edge.source, edge.target)] = getattr(edge, "weight", 1.0)
            wmap[(edge.target, edge.source)] = getattr(edge, "weight", 1.0)
        self._adjacency = dict(adj)
        self._weight_map = wmap

    def build_graph(self) -> dict:
        """构建完整语义图谱，返回 {nodes: [SemanticNode], edges: [SemanticRelation]}"""
        wiki_dir = paths.wiki_dir
        self._graph_cache = self.builder.build(str(wiki_dir))
        self._build_adjacency()
        assert self._graph_cache is not None
        return self._graph_cache

    def _ensure_graph(self) -> dict:
        if self._graph_cache is None:
            result = self.build_graph()
            return result if result is not None else {}
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
                if len(results) >= limit:
                    break
        return results[:limit]

    def related(self, node_id: str) -> list[dict]:
        """获取某个节点的关联节点（O(1) 查索引）"""
        self._ensure_graph()
        assert self._graph_cache is not None
        related_ids = self._adjacency.get(node_id, set())
        node_map = {n.id: n for n in self._graph_cache["nodes"]}
        results = []
        for rid in related_ids:
            if rid in node_map:
                results.append(node_map[rid])
            else:
                results.append(
                    {
                        "id": rid,
                        "title": rid,
                        "summary": "(被引用)",
                        "links": [],
                    }
                )
        return results

    # ── 属性 ──

    @property
    def node_count(self) -> int:
        return len(self._ensure_graph()["nodes"])

    @property
    def edge_count(self) -> int:
        return len(self._ensure_graph()["edges"])

    @property
    def adjacency(self) -> dict[str, set[str]]:
        """邻接索引：{node_id: {neighbor_id, ...}}"""
        self._ensure_graph()
        return self._adjacency

    @property
    def weight_map(self) -> dict[tuple[str, str], float]:
        """权重索引：{(source, target): weight} — O(1) 边权重查询"""
        self._ensure_graph()
        return self._weight_map

    def refresh(self) -> dict:
        """强制重建图谱"""
        self._graph_cache = None
        self._adjacency = {}
        self._weight_map = {}
        return self.build_graph()


# 单例（由 runtime.bootstrap 统一管理，此处仅作导入兼容）
from runtime.bootstrap import get_semantic as _get_semantic

semantic = _get_semantic()
