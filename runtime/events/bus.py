# 太初-事件总线
# Event Bus for Knowledge Universe Runtime
# 负责 websocket 推送 / 内部事件 / 订阅分发

from __future__ import annotations

import asyncio
import json
import logging
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any

logger = logging.getLogger("taichu.events")


class EventBus:
    """内存事件总线，支持同步订阅 + 异步 WebSocket 广播"""

    def __init__(self, max_workers: int = 4):
        self._handlers: dict[str, list[Callable]] = defaultdict(list)
        self._ws_clients: set[asyncio.Queue] = set()
        self._executor = ThreadPoolExecutor(max_workers)
        self._lock = threading.Lock()

    # ── 订阅 ──

    def subscribe(self, event: str, callback: Callable):
        with self._lock:
            self._handlers[event].append(callback)

    def on(self, event: str, callback: Callable):
        """subscribe 的别名"""
        self.subscribe(event, callback)

    def unsubscribe(self, event: str, callback: Callable):
        with self._lock:
            if event in self._handlers:
                self._handlers[event] = [c for c in self._handlers[event] if c is not callback]

    # ── 发布 ──

    def emit_sync(self, event_type: str, data: Any = None):
        """同步发射事件，等待所有处理器完成。用于事务关键场景。"""
        for handler in self._handlers.get(event_type, []):
            try:
                handler(data)
            except Exception as e:
                logger.error(f"EventBus handler error [{event_type}]: {e}")

    def emit_async(self, event_type: str, data: Any = None):
        """异步发射事件，立即返回，不阻塞当前线程。
        适合批量操作场景（如批量导入 100 个文件）。
        """
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
                dead.add(q)
        self._ws_clients -= dead

    def _safe_call(self, handler, data, event_type):
        try:
            handler(data)
        except Exception as e:
            logger.error(f"EventBus async error [{event_type}]: {e}")

    # ── WebSocket 管理 ──

    def add_ws_client(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=128)
        self._ws_clients.add(q)
        return q

    def remove_ws_client(self, q: asyncio.Queue):
        self._ws_clients.discard(q)


# 单例
bus = EventBus()
