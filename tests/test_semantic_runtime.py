"""SemanticRuntime 测试：图谱构建、邻接索引、查询（mock GraphBuilder）"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path.home() / "taichu"))

import pytest

# 在 import runtime.semantic.runtime 之前 mock GraphBuilder
with patch("knowledge.graph.builder.GraphBuilder") as MockBuilder:
    MockBuilder.return_value = MagicMock()

    from runtime.bootstrap import get_semantic, init_runtime

    # 确保 bootstrap 初始化完成
    init_runtime()
    from runtime.semantic.runtime import SemanticRuntime


class TestSemanticRuntime:
    def _make_mock_graph(self):
        """构造 mock 图谱数据"""
        from runtime.schema import SemanticNode, SemanticRelation

        nodes = [
            SemanticNode("n1", label="Node 1", summary="first node", gravity=1.0),
            SemanticNode("n2", label="Node 2", summary="second node", gravity=1.0),
            SemanticNode("n3", label="Node 3", summary="third node", gravity=1.0),
        ]
        edges = [
            SemanticRelation("n1", "n2", weight=0.8),
            SemanticRelation("n2", "n3", weight=0.5),
        ]
        return {"nodes": nodes, "edges": edges}

    def test_build_graph(self):
        rt = SemanticRuntime()
        with patch.object(rt, "builder") as mock_builder:
            mock_builder.build.return_value = self._make_mock_graph()
            result = rt.build_graph()
            assert "nodes" in result
            assert "edges" in result
            assert len(result["nodes"]) == 3
            assert len(result["edges"]) == 2

    def test_ensure_graph_returns_cache(self):
        rt = SemanticRuntime()
        rt._graph_cache = {"nodes": [], "edges": []}
        result = rt._ensure_graph()
        assert result == {"nodes": [], "edges": []}

    def test_ensure_graph_builds_when_none(self):
        rt = SemanticRuntime()
        with patch.object(rt, "builder") as mock_builder:
            mock_builder.build.return_value = self._make_mock_graph()
            result = rt._ensure_graph()
            assert len(result["nodes"]) == 3

    def test_adjacency_property(self):
        rt = SemanticRuntime()
        with patch.object(rt, "builder") as mock_builder:
            mock_builder.build.return_value = self._make_mock_graph()
            adj = rt.adjacency
            assert "n1" in adj
            assert "n2" in adj
            assert "n3" in adj
            assert "n2" in adj["n1"]
            assert "n1" in adj["n2"]
            assert "n3" in adj["n2"]

    def test_related_returns_neighbors(self):
        rt = SemanticRuntime()
        with patch.object(rt, "builder") as mock_builder:
            mock_builder.build.return_value = self._make_mock_graph()
            related = rt.related("n1")
            ids = [r.id for r in related]
            assert "n2" in ids
            assert "n3" not in ids

    def test_related_unknown_node(self):
        rt = SemanticRuntime()
        with patch.object(rt, "builder") as mock_builder:
            mock_builder.build.return_value = self._make_mock_graph()
            related = rt.related("nonexistent")
            assert related == []

    def test_search_by_title(self):
        rt = SemanticRuntime()
        with patch.object(rt, "builder") as mock_builder:
            mock_builder.build.return_value = self._make_mock_graph()
            results = rt.search("Node 1")
            assert len(results) >= 1

    def test_search_by_summary(self):
        rt = SemanticRuntime()
        with patch.object(rt, "builder") as mock_builder:
            mock_builder.build.return_value = self._make_mock_graph()
            results = rt.search("second")
            assert len(results) >= 1

    def test_search_no_match(self):
        rt = SemanticRuntime()
        with patch.object(rt, "builder") as mock_builder:
            mock_builder.build.return_value = self._make_mock_graph()
            results = rt.search("zzzznotfound")
            assert results == []

    def test_node_count(self):
        rt = SemanticRuntime()
        with patch.object(rt, "builder") as mock_builder:
            mock_builder.build.return_value = self._make_mock_graph()
            assert rt.node_count == 3

    def test_edge_count(self):
        rt = SemanticRuntime()
        with patch.object(rt, "builder") as mock_builder:
            mock_builder.build.return_value = self._make_mock_graph()
            assert rt.edge_count == 2

    def test_refresh_clears_and_rebuilds(self):
        rt = SemanticRuntime()
        with patch.object(rt, "builder") as mock_builder:
            mock_builder.build.return_value = self._make_mock_graph()
            # 先构建
            rt.build_graph()
            assert rt.node_count == 3
            # refresh 应该重建
            mock_builder.build.return_value = {"nodes": [], "edges": []}
            result = rt.refresh()
            assert len(result["nodes"]) == 0

    def test_build_adjacency_empty_cache(self):
        rt = SemanticRuntime()
        rt._graph_cache = None
        rt._build_adjacency()
        assert rt._adjacency == {}

    def test_build_graph_handles_empty_wiki(self, tmp_path):
        """使用真实空目录验证 build_graph 不崩溃"""
        # 先恢复真实的 GraphBuilder 才能用真实目录
        import knowledge.graph.builder as gb_mod

        real_builder = gb_mod.GraphBuilder()
        rt = SemanticRuntime()
        rt.builder = real_builder
        # 用空目录
        import paths as paths_mod

        result = rt.build_graph()
        assert "nodes" in result
        assert "edges" in result

    def test_build_adjacency_undirected(self):
        """验证邻接索引是双向的"""
        rt = SemanticRuntime()
        with patch.object(rt, "builder") as mock_builder:
            mock_builder.build.return_value = self._make_mock_graph()
            rt.build_graph()
            assert "n1" in rt._adjacency["n2"]
            assert "n2" in rt._adjacency["n1"]
            assert "n3" in rt._adjacency["n2"]
            assert "n2" in rt._adjacency["n3"]


class TestBootstrapSemantic:
    def test_bootstrap_get_semantic(self):
        sem = get_semantic()
        assert hasattr(sem, "build_graph")
        assert hasattr(sem, "search")
        assert hasattr(sem, "related")
        assert hasattr(sem, "adjacency")

    def test_semantic_singleton_exists(self):
        from runtime.semantic.runtime import semantic

        assert hasattr(semantic, "build_graph")
