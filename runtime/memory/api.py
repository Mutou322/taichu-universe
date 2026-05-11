# 太初-Memory Runtime API
# 所有 Agent / UI 通过此 API 读写知识库
# 底层调 storage/ 层（ChromaStore + Embedder），不直接操作 ChromaDB

from pathlib import Path
from typing import Optional

import sys
sys.path.insert(0, str(Path.home() / "taichu" / "config"))
sys.path.insert(0, str(Path.home() / "taichu"))
from paths import paths


class MemoryRuntime:
    """统一记忆运行时 API"""

    def __init__(self):
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
        embedder = self._get_embedder()
        store = self._get_store()
        q_emb = embedder.embed(query)
        results = None
        # 依次尝试多个 collection
        for col in ["kb_articles", "evomind", "taichu_memory"]:
            try:
                results = store.query_by_embedding(q_emb, limit=top_k, collection=col)
                if results.get("ids") and results["ids"][0]:
                    break
            except Exception:
                continue

        if results is None or not results["ids"] or not results["ids"][0]:
            return []

        items = []
        for i in range(len(results["ids"][0])):
            meta = results["metadatas"][0][i] if results["metadatas"] else {}
            items.append({
                "title": meta.get("source", results["ids"][0][i]),
                "score": 1.0 / (1.0 + results["distances"][0][i]) if results["distances"] else 0.0,
                "text": results["documents"][0][i] if results["documents"] else "",
            })
        return items

    # ── 存储 ──

    def store(self, doc_id: str, text: str, metadata: Optional[dict] = None) -> bool:
        """存入一条知识到 ChromaDB"""
        try:
            store = self._get_store()
            store.add(doc_id, text, metadata or {})

            # 触发事件
            import importlib
            hooks = importlib.import_module("runtime.memory.hooks")
            hooks.on_memory_store(doc_id, text, metadata)

            return True
        except Exception as e:
            print(f"[MemoryRuntime] store 失败: {e}")
            return False

    # ── 嵌入 ──

    def embed(self, text: str) -> list[float]:
        return self._get_embedder().embed(text)

    # ── 删除 ──

    def delete(self, doc_id: str) -> bool:
        try:
            self._get_store().delete(doc_id)

            # 触发事件
            import importlib
            hooks = importlib.import_module("runtime.memory.hooks")
            hooks.on_memory_delete(doc_id)

            return True
        except Exception as e:
            print(f"[MemoryRuntime] delete 失败: {e}")
            return False

    # ── 统计 ──

    @property
    def count(self) -> int:
        try:
            return self._get_store().count
        except Exception:
            return 0


# 单例
memory = MemoryRuntime()
