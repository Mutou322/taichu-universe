"""语义图谱构建器 — 将 wiki 编译为图结构."""

import re
from collections import defaultdict
from pathlib import Path

from knowledge.graph.node import SemanticNode
from knowledge.relations.relation import RelationType, SemanticRelation
from knowledge.wiki.compiler import WikiCompiler


class GraphBuilder:
    """构建完整的语义图谱."""

    def __init__(self):
        self.compiler = WikiCompiler()
        self.nodes: dict[str, SemanticNode] = {}
        self.edges: list[SemanticRelation] = []

    def build(self, wiki_dir: str | Path) -> dict:
        """扫描 wiki 目录，返回 {nodes: [SemanticNode], edges: [SemanticRelation]}."""
        wiki_path = Path(wiki_dir)
        self.nodes = {}
        self.edges = []

        # 第一遍：编译所有文件
        for file in sorted(wiki_path.glob("*.md")):
            if file.stem == "index":
                continue
            try:
                node = self.compiler.compile(file)
                self.nodes[node.id] = node
            except Exception as e:
                print(f"[GraphBuilder] 跳过 {file.name}: {e}")

        # 第二遍：构建边
        edge_set: set[tuple[str, str, str]] = set()
        for node in self.nodes.values():
            for link in node.links:
                target = link.split("|")[0].strip()
                if not target:
                    continue
                key = (node.id, target, RelationType.REFERENCES.value)
                if key in edge_set:
                    continue
                edge_set.add(key)
                self.edges.append(
                    SemanticRelation(
                        source=node.id,
                        target=target,
                        relation_type=RelationType.REFERENCES.value,
                        weight=1.0,
                    )
                )

        # 为未创建的引用节点添加 stub
        for edge in self.edges:
            if edge.target not in self.nodes:
                self.nodes[edge.target] = SemanticNode(
                    id=edge.target,
                    title=edge.target,
                    content="",
                    links=[],
                    category="unknown_ref",
                    summary="(被引用但未创建)",
                )

        # 第三遍：基于内容相似度连接低度节点（在 common-neighbor 之前，
        # 避免节点被过多边抬高 degree 而失去资格）
        similar_edges = self._connect_by_similarity(self.nodes, self.edges, threshold=0.2, max_degree=3)
        self.edges.extend(similar_edges)

        # 第四遍：基于共同邻居推断潜在关系
        inferred = self.suggest_relations(threshold=2)
        for rel in inferred:
            self.edges.append(
                SemanticRelation(
                    source=rel["node_a"],
                    target=rel["node_b"],
                    relation_type="INFERRED",
                    weight=rel["strength"] / 10.0,
                )
            )

        return {
            "nodes": list(self.nodes.values()),
            "edges": self.edges,
        }

    def suggest_relations(self, threshold: int = 2) -> list:
        """基于共同邻居发现潜在关系.
        threshold: 共同邻居数 >= 该值时建议关联
        返回 [{"node_a": id, "node_b": id, "common_neighbors": [ids], "strength": int}]
        """
        if not self.edges:
            return []

        # 构建邻接表
        adjacency = defaultdict(set)
        for edge in self.edges:
            adjacency[edge.source].add(edge.target)
            adjacency[edge.target].add(edge.source)

        # 已直连的节点对
        existing = set()
        for edge in self.edges:
            pair = tuple(sorted([edge.source, edge.target]))
            existing.add(pair)

        suggestions = []
        # 只对非 stub 节点做推断
        real_nodes = [nid for nid, n in self.nodes.items() if n.category != "unknown_ref"]

        for i in range(len(real_nodes)):
            for j in range(i + 1, len(real_nodes)):
                a, b = real_nodes[i], real_nodes[j]
                if tuple(sorted([a, b])) in existing:
                    continue
                common = adjacency[a] & adjacency[b]
                if len(common) >= threshold:
                    suggestions.append(
                        {
                            "node_a": a,
                            "node_b": b,
                            "common_neighbors": list(common),
                            "strength": len(common),
                        }
                    )

        return suggestions

    def _connect_by_similarity(
        self,
        nodes: dict[str, SemanticNode],
        edges: list[SemanticRelation],
        threshold: float = 0.3,
        max_degree: int = 3,
    ) -> list[SemanticRelation]:
        """基于内容相似度连接低度节点，返回新增的 SIMILAR_TO 边."""
        if not edges:
            return []

        # 构建邻接表计算 degree
        adj = defaultdict(set)
        for e in edges:
            adj[e.source].add(e.target)
            adj[e.target].add(e.source)

        # 已直连的节点对
        existing = set()
        for e in edges:
            pair = tuple(sorted([e.source, e.target]))
            existing.add(pair)

        # 筛选 eligible 节点：低度且非 stub
        eligible = {}
        for nid, n in nodes.items():
            if n.category == "unknown_ref":
                continue
            degree = len(adj.get(nid, set()))
            if degree >= max_degree:
                continue
            words = set(w for w in re.split(r"\W+", f"{n.title} {n.summary} {' '.join(n.tags)}".lower()) if len(w) > 1)
            if words:
                eligible[nid] = words

        ids = list(eligible.keys())
        new_edges = []

        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                a, b = ids[i], ids[j]
                if tuple(sorted([a, b])) in existing:
                    continue
                set_a, set_b = eligible[a], eligible[b]
                intersection = set_a & set_b
                if not intersection:
                    continue
                union = set_a | set_b
                jaccard = len(intersection) / len(union)
                if jaccard >= threshold:
                    new_edges.append(
                        SemanticRelation(
                            source=a,
                            target=b,
                            relation_type=RelationType.SIMILAR_TO.value,
                            weight=min(jaccard * 2.0, 1.0),
                        )
                    )

        return new_edges
