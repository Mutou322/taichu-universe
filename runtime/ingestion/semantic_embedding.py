# runtime/ingestion/semantic_embedding.py

import numpy as np


class SemanticEmbedder:

    def __init__(self):

        self.model = None
        self._loaded = False

    def embed_documents(self, docs):

        if not docs:
            return np.array([])

        if not self._loaded:
            try:
                from sentence_transformers import SentenceTransformer

                self.model = SentenceTransformer("all-MiniLM-L6-v2")
                self._loaded = True
            except ImportError:
                return np.array([[0.0]] * len(docs))

        embeddings = self.model.encode(docs)

        return np.array(embeddings)
