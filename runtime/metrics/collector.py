"""指标采集器，记录检索历史并生成汇总统计"""

from .counters import metrics_counters


class MetricsCollector:
    """采集检索性能指标，维护历史记录并提供汇总能力"""

    def __init__(self) -> None:
        self.retrieval_history: list = []

    def record_retrieval(self, metrics) -> None:
        self.retrieval_history.append(metrics)

        if len(self.retrieval_history) > 1000:
            self.retrieval_history.pop(0)

    def summary(self) -> dict:
        total = len(self.retrieval_history)

        if total == 0:
            return {}

        avg_latency = sum(m.total_ms for m in self.retrieval_history) / total

        return {"queries": total, "avg_latency_ms": avg_latency, "counters": metrics_counters.snapshot()}


metrics_collector = MetricsCollector()
