# runtime/ingestion/data_ingest.py

import asyncio

from runtime.ingestion.feed_parser import FeedParser
from runtime.ingestion.ocr_vision import OCRVision
from runtime.ingestion.semantic_embedding import SemanticEmbedder


class DataIngest:

    def __init__(self, sources):

        self.sources = sources
        self.parser = FeedParser()
        self.ocr = OCRVision()

    async def ingest(self):

        documents = []

        for src in self.sources:

            raw_data = await src.fetch()

            text = await self.parser.parse(raw_data)

            ocr_text = await self.ocr.extract(raw_data)

            combined = text + " " + ocr_text

            documents.append(combined)

        return documents


class ContinuousIngest:

    def __init__(self, sources, graph):

        self.sources = sources
        self.graph = graph
        self.embedder = SemanticEmbedder()

    async def run(self):

        while True:

            documents = []

            for src in self.sources:

                raw_data = await src.fetch()

                documents.append(raw_data)

            embeddings = self.embedder.embed_documents(documents)

            for doc, emb in zip(documents, embeddings):

                self.graph.add_node(doc, embedding=emb)

            await asyncio.sleep(2)
