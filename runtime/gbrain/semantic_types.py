"""语义类型定义 — SemanticNode 和 SemanticRelation 数据类"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SemanticNode:
    id: str
    label: str
    gravity: float = 1.0
    retrieval_hits: int = 0
    visit_count: int = 0
    centrality: float = 0.0
    recency_score: float = 1.0
    relations: List[str] = field(default_factory=list)
    clusters: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class SemanticRelation:
    source: str
    target: str
    relation_type: str
    confidence: float = 0.5
    weight: float = 1.0
