"""Ingestion 结果数据结构"""

from dataclasses import dataclass
from typing import Any


@dataclass
class IngestResult:
    """单次 ingestion 的结果，包含文本内容、模态类型和元数据"""

    text: str
    modality: str
    metadata: dict[str, Any]
