from dataclasses import dataclass, field
from typing import List


@dataclass
class SemanticNode:
    """语义节点 — 知识宇宙的基本单元"""

    # 节点唯一 ID（文件名 stem）
    id: str

    # 节点标题
    title: str

    # 完整 Markdown 内容
    content: str

    # 双链关系
    links: List[str] = field(default_factory=list)

    # 标签
    tags: List[str] = field(default_factory=list)

    # 语义类别
    category: str = "concept"

    # 摘要（第一行非空非标题文本）
    summary: str = ""

    # 热度（未来用于星云引力）
    heat: float = 0.0
