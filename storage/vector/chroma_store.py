"""ChromaStore — 向量存储层

职责：封装 ChromaDB 的所有细节。
上层（Runtime）不知道 ChromaDB 的存在，只知道 VectorStore。
"""

import chromadb
from pathlib import Path
from typing import Optional


class ChromaStore:
    """ChromaDB 向量存储封装"""

    def __init__(self, path: str, collection_name: str = "taichu_memory"):
        self.client = chromadb.PersistentClient(path=path)
        self.collection_name = collection_name
        self._collection = None

    def _get_collection(self, name: str = None):
        name = name or self.collection_name
        if self._collection is None or self._collection.name != name:
            try:
                self._collection = self.client.get_collection(name)
            except Exception:
                self._collection = self.client.create_collection(name)
        return self._collection

    # ── 写 ──

    def add(self, doc_id: str, content: str, metadata: Optional[dict] = None):
        meta = metadata if metadata else {"source": doc_id}
        self._get_collection().add(
            ids=[doc_id],
            documents=[content],
            metadatas=[meta],
        )

    def add_with_embedding(self, doc_id: str, content: str, embedding: list[float],
                           metadata: Optional[dict] = None):
        self._get_collection().add(
            ids=[doc_id],
            documents=[content],
            embeddings=[embedding],
            metadatas=[metadata or {}],
        )

    # ── 读 ──

    def query(self, text: str, limit: int = 10) -> dict:
        return self._get_collection().query(
            query_texts=[text],
            n_results=min(limit, 50),
        )

    def query_by_embedding(self, embedding: list[float], limit: int = 10,
                           collection: str = None) -> dict:
        return self._get_collection(collection).query(
            query_embeddings=[embedding],
            n_results=min(limit, 50),
        )

    # ── 删 ──

    def delete(self, doc_id: str):
        self._get_collection().delete(ids=[doc_id])

    # ── 统计 ──

    @property
    def count(self) -> int:
        return self._get_collection().count()
