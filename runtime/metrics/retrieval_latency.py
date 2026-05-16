import time
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class RetrievalMetrics:
    query: str

    parse_ms: float = 0
    vector_ms: float = 0
    graph_ms: float = 0
    rerank_ms: float = 0
    context_ms: float = 0

    total_ms: float = 0

    result_count: int = 0
    graph_nodes_expanded: int = 0

    created_at: float = field(default_factory=time.time)

    def to_dict(self):
        return self.__dict__
