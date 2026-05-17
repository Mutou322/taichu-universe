"""检索延迟数据模型，记录一次检索各阶段的耗时与结果统计"""

import time
from dataclasses import dataclass, field


@dataclass
class RetrievalMetrics:
    """单次检索的性能指标，覆盖解析、向量、图谱、重排序等各阶段"""

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

    def to_dict(self) -> dict:
        return self.__dict__
