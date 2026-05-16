from collections import defaultdict
from threading import Lock


class MetricsCounters:
    def __init__(self):
        self.counters = defaultdict(int)
        self.lock = Lock()

    def increment(self, name: str, amount: int = 1):
        with self.lock:
            self.counters[name] += amount

    def get(self, name: str):
        return self.counters.get(name, 0)

    def snapshot(self):
        return dict(self.counters)


metrics_counters = MetricsCounters()
