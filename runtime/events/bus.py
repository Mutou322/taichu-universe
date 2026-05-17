"""太初知识宇宙 — 内存事件总线，支持同步/异步事件发布订阅与 WebSocket 广播"""

from __future__ import annotations

import asyncio
import logging
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

from runtime.metrics.counters import metrics_counters

logger = logging.getLogger("taichu.events")


class EventBus:
    """内存事件总线，支持同步订阅 + 异步 WebSocket 广播"""

    def __init__(self, max_workers: int = 4) -> None:
        self._handlers: dict[str, list[Callable]] = defaultdict(list)
        self._ws_clients: set[asyncio.Queue] = set()
        self._executor = ThreadPoolExecutor(max_workers)
        self._lock = threading.Lock()

    # ── 订阅 ──

    def subscribe(self, event: str, callback: Callable) -> None:
        with self._lock:
            self._handlers[event].append(callback)

    def on(self, event: str, callback: Callable) -> None:
        """subscribe 的别名"""
        self.subscribe(event, callback)

    def unsubscribe(self, event: str, callback: Callable) -> None:
        with self._lock:
            if event in self._handlers:
                self._handlers[event] = [c for c in self._handlers[event] if c is not callback]

    # ── 发布 ──

    def emit_sync(self, event_type: str, data: Any = None) -> None:
        """同步发射事件，等待所有处理器完成。用于事务关键场景。"""
        handlers = self._handlers.get(event_type, [])
        metrics_counters.increment(f"eventbus.emit_sync.{event_type}")
        metrics_counters.increment("eventbus.total_emits")
        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                logger.error(f"EventBus handler error [{event_type}]: {e}")

    def emit_async(self, event_type: str, data: Any = None) -> None:
        """异步发射事件，立即返回，不阻塞当前线程。
        适合批量操作场景（如批量导入 100 个文件）。
        """
        metrics_counters.increment(f"eventbus.emit_async.{event_type}")
        metrics_counters.increment("eventbus.total_emits")
        with self._lock:
            handlers = list(self._handlers.get(event_type, []))
        for handler in handlers:
            self._executor.submit(self._safe_call, handler, data, event_type)

    async def emit(self, event_type: str, data: Any = None):
        """异步协程发布事件（含 WebSocket 广播）"""
        self.emit_sync(event_type, data)
        payload = {"event": event_type, "data": data}

        # WebSocket 广播
        dead = set()
        for q in self._ws_clients:
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                try:
                    await asyncio.sleep(0.1)
                    q.put_nowait(payload)
                except asyncio.QueueFull:
                    dead.add(q)
        self._ws_clients -= dead

    def shutdown(self) -> None:
        self._executor.shutdown(wait=False)

    def _safe_call(self, handler: Callable, data: Any, event_type: str) -> None:
        try:
            handler(data)
        except Exception as e:
            logger.error(f"EventBus async error [{event_type}]: {e}")

    # ── WebSocket 管理 ──

    def add_ws_client(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=128)
        self._ws_clients.add(q)
        return q

    def remove_ws_client(self, q: asyncio.Queue) -> None:
        self._ws_clients.discard(q)


# 单例
bus = EventBus()
