"""数据摄取 — 从多个数据源拉取、解析、OCR 并组装文档"""

import asyncio
import logging
from typing import Any

from runtime.ingestion.feed_parser import FeedParser
from runtime.ingestion.ocr_vision import OCRVision
from runtime.ingestion.semantic_embedding import SemanticEmbedder

logger = logging.getLogger(__name__)


class DataIngest:
    """一次性批量摄取：拉取→解析→OCR→合并"""

    def __init__(self, sources: list[Any]) -> None:

        self.sources = sources
        self.parser = FeedParser()
        self.ocr = OCRVision()

    async def ingest(self) -> list[str]:
        """遍历所有数据源，完成拉取+解析+OCR，返回合并后的文档列表"""
        documents: list[str] = []

        for src in self.sources:

            raw_data = await src.fetch()

            text = await self.parser.parse(raw_data)

            ocr_text = await self.ocr.extract(raw_data)

            combined = text + " " + ocr_text

            documents.append(combined)

        return documents


class ContinuousIngest:
    """持续摄取服务：循环拉取数据源并嵌入写入图谱"""

    def __init__(self, sources: list[Any], graph: Any) -> None:

        self.sources = sources
        self.graph = graph
        self.embedder = SemanticEmbedder()
        self._stop_event = asyncio.Event()

    async def stop(self) -> None:
        self._stop_event.set()

    async def run(self) -> None:
        """循环拉取→嵌入→写入图谱，直到收到停止信号"""
        while not self._stop_event.is_set():

            documents = []

            for src in self.sources:
                try:
                    raw_data = await asyncio.wait_for(src.fetch(), timeout=30)
                    documents.append(raw_data)
                except asyncio.TimeoutError:
                    logger.warning("source fetch timeout: %s", src)
                    continue
                except Exception as e:
                    logger.warning("source fetch error: %s", e)
                    continue

            if not documents:
                await asyncio.sleep(2)
                continue

            try:
                embeddings = self.embedder.embed_documents(documents)

                for doc, emb in zip(documents, embeddings):
                    self.graph.add_node(doc, embedding=emb)
            except Exception as e:
                logger.warning("embedding error: %s", e)

            await asyncio.sleep(2)
