"""线程安全的原子计数器，用于全局指标计数"""

from collections import defaultdict
from threading import Lock


class MetricsCounters:
    """线程安全的名值计数器，支持增减和快照"""

    def __init__(self) -> None:
        self.counters: defaultdict[str, int] = defaultdict(int)
        self.lock = Lock()

    def increment(self, name: str, amount: int = 1) -> None:
        with self.lock:
            self.counters[name] += amount

    def get(self, name: str) -> int:
        return self.counters.get(name, 0)

    def snapshot(self) -> dict:
        return dict(self.counters)


metrics_counters = MetricsCounters()
