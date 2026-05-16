"""
太初知识宇宙 — 基础测试集

运行方式:
    cd ~/taichu && python3 -m pytest tests/ -v
"""

import sys
from pathlib import Path

# 确保路径
TAICHU_CONFIG = Path.home() / "taichu" / "config"
TAICHU_HOME = Path.home() / "taichu"
for p in [str(TAICHU_CONFIG), str(TAICHU_HOME)]:
    if p not in sys.path:
        sys.path.insert(0, p)


class TestConfig:
    """配置系统测试"""

    def test_paths_import(self):
        from paths import paths

        assert hasattr(paths, "wiki_dir")
        assert paths.wiki_dir.exists()

    def test_models_import(self):
        from models import models

        cfg = models.get("compile")
        assert cfg is not None
        assert "model" in cfg
        assert "api_key" in cfg

    def test_models_list(self):
        from models import models

        ml = models.list_models()
        assert "compile" in ml
        assert "embedding" in ml

    def test_paths_chain_access(self):
        """测试 paths.ingest.inbox 链式访问"""
        from paths import paths

        inbox = paths.ingest.inbox
        assert str(inbox).endswith("ingest/inbox")


class TestBootstrap:
    """bootstrap 测试"""

    def test_init_runtime(self):
        from runtime.bootstrap import init_runtime

        ctx = init_runtime()
        assert "paths" in ctx
        assert "models" in ctx
        assert "logger" in ctx

    def test_get_memory(self):
        from runtime.bootstrap import get_memory

        mem = get_memory()
        assert hasattr(mem, "search")
        assert hasattr(mem, "store")


class TestSchema:
    """Schema 统一测试"""

    def test_semantic_node(self):
        from runtime.schema import SemanticNode

        n = SemanticNode("test-id", label="测试", gravity=2.5)
        assert n.id == "test-id"
        assert n.gravity == 2.5

    def test_semantic_relation(self):
        from runtime.schema import SemanticRelation

        e = SemanticRelation("src", "tgt", weight=0.8)
        assert e.source == "src"
        assert e.target == "tgt"
        assert e.weight == 0.8

    def test_normalize_retrieval_doc(self):
        from runtime.schema import normalize_retrieval_doc

        doc = {"graph_score": 0.9, "final_score": 0.5}
        normalize_retrieval_doc(doc)
        assert doc.get("graph_centrality") == 0.9

    def test_safe_import_success(self):
        from runtime.schema import safe_import

        mod = safe_import("json")
        assert mod is not None

    def test_safe_import_fallback(self):
        from runtime.schema import safe_import

        mod = safe_import("nonexistent_module_xyz")
        assert mod is None


class TestRetrieval:
    """检索模块测试"""

    def test_rerank_docs_empty(self):
        from runtime.retrieval.rerank import rerank_docs

        result = rerank_docs([])
        assert result == []

    def test_rerank_docs_basic(self):
        from runtime.retrieval.rerank import rerank_docs

        docs = [
            {"id": "a", "final_score": 0.8, "graph_centrality": 0.6},
            {"id": "b", "final_score": 0.6, "graph_centrality": 0.9},
        ]
        result = rerank_docs(docs)
        assert len(result) == 2
        # b 应该排在前面 (0.6*0.6 + 0.4*0.9 = 0.72 > 0.6*0.8 + 0.4*0.6 = 0.72... 相同时保持原序)
        assert result[0]["rerank_score"] >= result[1]["rerank_score"]

    def test_rerank_handles_old_field(self):
        """rerank 应该兼容旧的 graph_score 字段"""
        from runtime.retrieval.rerank import rerank_docs

        docs = [
            {"id": "a", "final_score": 0.7, "graph_score": 0.8},
        ]
        result = rerank_docs(docs)
        assert "rerank_score" in result[0]
