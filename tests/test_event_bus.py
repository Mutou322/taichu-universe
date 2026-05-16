"""EventBus 测试：订阅、发布、WebSocket 队列"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "taichu"))

import asyncio

import pytest

from runtime.events.bus import EventBus


class TestEventBus:
    def test_subscribe_and_emit_sync(self):
        bus = EventBus()
        received = []
        bus.subscribe("test:event", lambda d: received.append(d))
        bus.emit_sync("test:event", {"key": "val"})
        assert received == [{"key": "val"}]

    def test_on_alias(self):
        bus = EventBus()
        received = []
        bus.on("test:event", lambda d: received.append(d))
        bus.emit_sync("test:event", "data")
        assert received == ["data"]

    def test_unsubscribe(self):
        bus = EventBus()

        def listener(data):
            pass

        bus.subscribe("t", listener)
        assert len(bus._handlers["t"]) == 1
        bus.unsubscribe("t", listener)
        assert len(bus._handlers["t"]) == 0

    def test_emit_sync_no_handler_no_crash(self):
        bus = EventBus()
        bus.emit_sync("nonexistent", "data")  # should not crash

    def test_handler_error_isolation(self):
        bus = EventBus()
        results = []

        def bad(data):
            raise ValueError("oops")

        def good(data):
            results.append(data)

        bus.subscribe("t", bad)
        bus.subscribe("t", good)
        bus.emit_sync("t", "ok")
        assert results == ["ok"]

    def test_emit_sync_multiple_handlers(self):
        bus = EventBus()
        results = []

        def a(d):
            results.append("a" + str(d))

        def b(d):
            results.append("b" + str(d))

        bus.subscribe("t", a)
        bus.subscribe("t", b)
        bus.emit_sync("t", 1)
        assert results == ["a1", "b1"]

    @pytest.mark.asyncio
    async def test_emit_async(self):
        bus = EventBus()
        received = []
        bus.subscribe("t", lambda d: received.append(d))
        await bus.emit("t", "data")
        assert received == ["data"]

    @pytest.mark.asyncio
    async def test_emit_broadcasts_to_ws_queues(self):
        bus = EventBus()
        q1 = bus.add_ws_client()
        q2 = bus.add_ws_client()
        await bus.emit("ws_test", {"n": 1})
        result1 = await asyncio.wait_for(q1.get(), timeout=1)
        result2 = await asyncio.wait_for(q2.get(), timeout=1)
        expected = {"event": "ws_test", "data": {"n": 1}}
        assert result1 == expected
        assert result2 == expected

    @pytest.mark.asyncio
    async def test_remove_ws_client(self):
        bus = EventBus()
        q = bus.add_ws_client()
        bus.remove_ws_client(q)
        assert q not in bus._ws_clients

    @pytest.mark.asyncio
    async def test_ws_queue_maxsize(self):
        bus = EventBus()
        q = bus.add_ws_client()
        assert q.maxsize == 128

    def test_emit_sync_increments_counter(self):
        bus = EventBus()
        from runtime.metrics.counters import metrics_counters

        before = metrics_counters.get("eventbus.total_emits") or 0
        bus.emit_sync("t", 1)
        after = metrics_counters.get("eventbus.total_emits") or 0
        assert after == before + 1

    def test_global_singleton_exists(self):
        from runtime.events.bus import bus

        assert hasattr(bus, "subscribe")
        assert hasattr(bus, "emit_sync")
        assert hasattr(bus, "emit")
