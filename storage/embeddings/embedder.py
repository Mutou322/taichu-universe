"""Embedder — 文本嵌入层

职责：封装 embedding 模型的细节。
上层（Runtime）不需要知道用的是哪个模型。
"""

from sentence_transformers import SentenceTransformer


class Embedder:
    """文本嵌入器（单例 + 延迟加载）"""

    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.model_name = model_name
        self._model = None

    def _load(self):
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)

    def embed(self, text: str) -> list[float]:
        """单个文本 → 向量"""
        self._load()
        return self._model.encode(text).tolist()

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        """批量文本 → 向量"""
        self._load()
        return self._model.encode(texts).tolist()
