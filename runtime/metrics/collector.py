from .counters import metrics_counters


class MetricsCollector:
    def __init__(self):
        self.retrieval_history = []

    def record_retrieval(self, metrics):
        self.retrieval_history.append(metrics)

        if len(self.retrieval_history) > 1000:
            self.retrieval_history.pop(0)

    def summary(self):
        total = len(self.retrieval_history)

        if total == 0:
            return {}

        avg_latency = sum(m.total_ms for m in self.retrieval_history) / total

        return {"queries": total, "avg_latency_ms": avg_latency, "counters": metrics_counters.snapshot()}


metrics_collector = MetricsCollector()
