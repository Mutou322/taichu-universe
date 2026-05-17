"""语义嵌入 — 使用 SentenceTransformer 将文档批量编码为向量"""

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


class SemanticEmbedder:
    """延迟加载 SentenceTransformer 模型，批量编码文档为 numpy 向量"""

    def __init__(self) -> None:

        self.model: Any = None
        self._loaded = False

    def embed_documents(self, docs: list[str]) -> np.ndarray:
        """批量编码文档列表，首次调用时自动加载 all-MiniLM-L6-v2 模型"""
        if not docs:
            return np.array([])

        if not self._loaded:
            try:
                from sentence_transformers import SentenceTransformer

                self.model = SentenceTransformer("all-MiniLM-L6-v2")
                self._loaded = True
            except ImportError:
                logger.error("sentence_transformers 不可用，嵌入返回空数组")
                return np.array([])

        embeddings = self.model.encode(docs)

        return np.array(embeddings)
