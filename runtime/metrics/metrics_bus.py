import asyncio
from collections import defaultdict
from typing import Callable, Dict, List

from .models import MetricEvent


class MetricsBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.data_store: Dict[str, list] = defaultdict(list)

    def subscribe(self, topic: str, callback: Callable):
        self.subscribers[topic].append(callback)

    def emit(self, topic: str, data):
        self.data_store[topic].append(data)
        for cb in self.subscribers[topic]:
            try:
                cb(data)
            except Exception as e:
                print(f"[MetricsBus] sync listener error: {e}")

    def emit_sync(self, topic: str, data):
        """同步发射（无事件循环时的兜底）"""
        self.data_store[topic].append(data)
        for cb in self.subscribers[topic]:
            try:
                cb(data)
            except Exception as e:
                print(f"[MetricsBus] sync listener error: {e}")

    async def emit_async(self, topic: str, data):
        self.data_store[topic].append(data)
        for cb in self.subscribers[topic]:
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb(data)
                else:
                    cb(data)
            except Exception as e:
                print(f"[MetricsBus] async listener error: {e}")


metrics_bus = MetricsBus()
