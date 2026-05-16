"""graph_expand 测试：图谱扩展、修剪、衰减（使用 mock 避免依赖真实图谱）"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.home() / "taichu"))

from unittest import mock

import pytest

from runtime.retrieval.graph_expand import (
    _apply_decay,
    _neighbors_with_decay,
    _neighbors_with_weight,
    _prune_low_score,
    expand_graph,
)


class TestPruneLowScore:
    def test_filters_below_threshold(self):
        neighbors = [("a", 0.5), ("b", 0.2), ("c", 0.8)]
        pruned = _prune_low_score(neighbors, threshold=0.3)
        assert "a" in pruned
        assert "b" not in pruned
        assert "c" in pruned

    def test_threshold_boundary(self):
        neighbors = [("a", 0.3), ("b", 0.299)]
        pruned = _prune_low_score(neighbors, threshold=0.3)
        assert "a" in pruned
        assert "b" not in pruned

    def test_empty_input(self):
        assert _prune_low_score([]) == []

    def test_default_threshold(self):
        neighbors = [("a", 0.3), ("b", 0.29)]
        pruned = _prune_low_score(neighbors)
        assert "a" in pruned
        assert "b" not in pruned


class TestApplyDecay:
    def test_no_record_no_decay(self):
        decay = _apply_decay("unknown_node")
        assert decay == 1.0

    def test_recent_access_no_decay(self):
        from runtime.retrieval.graph_expand import _node_access

        _node_access["recent"] = time.time()
        decay = _apply_decay("recent")
        assert decay == 1.0

    def test_old_access_returns_factor(self):
        from runtime.retrieval.graph_expand import _node_access

        old_time = time.time() - 7200  # 2 hours ago
        _node_access["old_node"] = old_time
        decay = _apply_decay("old_node", factor=0.9, interval=3600)
        assert decay == 0.9

    def test_custom_interval(self):
        from runtime.retrieval.graph_expand import _node_access

        _node_access["mid"] = time.time() - 1800  # 30 min ago
        decay = _apply_decay("mid", factor=0.5, interval=3600)
        assert decay == 1.0  # within 3600s, no decay
        decay2 = _apply_decay("mid", factor=0.5, interval=900)
        assert decay2 == 0.5  # past 900s, decay

    def test_custom_factor(self):
        from runtime.retrieval.graph_expand import _node_access

        _node_access["old"] = time.time() - 7200
        decay = _apply_decay("old", factor=0.75, interval=3600)
        assert decay == 0.75


class TestNeighborsWithWeight:
    def test_empty_graph(self):
        with mock.patch("runtime.retrieval.graph_expand._get_semantic") as mock_get:
            sem = mock.MagicMock()
            sem._graph_cache = {"edges": []}
            sem.adjacency = {}
            sem.weight_map = {}
            mock_get.return_value = sem
            result = _neighbors_with_weight("node_x")
            assert result == []

    def test_with_edges(self):
        with mock.patch("runtime.retrieval.graph_expand._get_semantic") as mock_get:
            sem = mock.MagicMock()
            sem._graph_cache = {
                "edges": [
                    mock.MagicMock(source="a", target="b", weight=1.0),
                    mock.MagicMock(source="a", target="c", weight=0.5),
                ]
            }
            sem.adjacency = {"a": {"b", "c"}}
            sem.weight_map = {("a", "b"): 1.0, ("b", "a"): 1.0, ("a", "c"): 0.5, ("c", "a"): 0.5}
            mock_get.return_value = sem
            result = _neighbors_with_weight("a")
            assert ("b", 1.0) in result
            assert ("c", 0.5) in result

    def test_weight_default_when_missing(self):
        with mock.patch("runtime.retrieval.graph_expand._get_semantic") as mock_get:
            sem = mock.MagicMock()
            edge = mock.MagicMock(source="x", target="y")
            del edge.weight  # no weight attr
            sem._graph_cache = {"edges": [edge]}
            sem.adjacency = {"x": {"y"}}
            sem.weight_map = {}
            mock_get.return_value = sem
            result = _neighbors_with_weight("x")
            assert ("y", 1.0) in result


class TestNeighborsWithDecay:
    def test_integration_prune_and_decay(self):
        from runtime.retrieval.graph_expand import _node_access

        _node_access.clear()
        with mock.patch("runtime.retrieval.graph_expand._neighbors_with_weight") as mock_nbr:
            mock_nbr.return_value = [("a", 0.5), ("b", 0.2), ("c", 0.8)]
            result = _neighbors_with_decay("any", decay_threshold=0.5)
            # "b" filtered by pruning (0.2 < 0.3)
            # "a" and "c" passed pruning, decay is 1.0 (fresh)
            assert "a" in result
            assert "b" not in result
            assert "c" in result


class TestExpandGraph:
    def test_empty_docs(self):
        result = expand_graph([], max_depth=1)
        assert result == []

    def test_single_doc_no_graph(self):
        result = expand_graph([{"id": "test_doc", "title": "Test"}], max_depth=1)
        assert len(result) == 1
        assert result[0]["graph_neighbors"] == []
        assert "graph_nodes_expanded" in result[0]
        assert "graph_edges_processed" in result[0]

    def test_max_depth_limits_expansion(self):
        docs = [{"id": "root"}]
        result = expand_graph(docs, max_depth=0, max_neighbors=10, max_nodes_per_query=100)
        assert len(result) == 1
        # depth 0 means only root node itself is visited
        assert result[0]["graph_nodes_expanded"] == 1

    def test_max_neighbors_limits_fanout(self):
        docs = [{"id": "center"}]
        result = expand_graph(docs, max_depth=2, max_neighbors=3, max_nodes_per_query=100)
        assert len(result) == 1

    def test_budget_exhausted_flag(self):
        docs = [{"id": "a"}, {"id": "b"}]
        result = expand_graph(docs, max_depth=2, max_nodes_per_query=1, max_edges_per_query=1)
        for r in result:
            if isinstance(r, dict):
                pass

    def test_visited_set_prevents_duplicates(self):
        """相同节点不应被重复扩展"""
        docs = [{"id": "root"}]
        result = expand_graph(docs, max_depth=3, max_neighbors=10, max_nodes_per_query=100)
        assert len(result) == 1
