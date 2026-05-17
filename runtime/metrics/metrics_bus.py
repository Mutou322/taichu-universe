"""指标消息总线，支持同步和异步的主题订阅与发布"""

import asyncio
import logging
from collections import defaultdict
from typing import Callable

logger = logging.getLogger(__name__)


class MetricsBus:
    """主题式指标事件总线，支持同步/异步发射与回调注册"""

    def __init__(self):
        self.subscribers: dict[str, list[Callable]] = defaultdict(list)
        self.data_store: dict[str, list] = defaultdict(list)

    def subscribe(self, topic: str, callback: Callable) -> None:
        self.subscribers[topic].append(callback)

    def emit(self, topic: str, data) -> None:
        self.data_store[topic].append(data)
        for cb in self.subscribers[topic]:
            try:
                cb(data)
            except Exception as e:
                logger.warning("sync listener error: %s", e)

    def emit_sync(self, topic: str, data) -> None:
        """同步发射（无事件循环时的兜底）"""
        self.data_store[topic].append(data)
        for cb in self.subscribers[topic]:
            try:
                cb(data)
            except Exception as e:
                logger.warning("sync listener error: %s", e)

    async def emit_async(self, topic: str, data) -> None:
        self.data_store[topic].append(data)
        for cb in self.subscribers[topic]:
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb(data)
                else:
                    cb(data)
            except Exception as e:
                logger.warning("async listener error: %s", e)


metrics_bus = MetricsBus()
