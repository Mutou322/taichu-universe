"""MetricsBus 测试：发射、订阅、错误隔离"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "taichu"))

import pytest

from runtime.metrics.metrics_bus import MetricsBus


class TestMetricsBus:
    def test_emit_stores_data(self):
        bus = MetricsBus()
        bus.emit("test_topic", {"msg": "hello"})
        assert len(bus.data_store["test_topic"]) == 1
        assert bus.data_store["test_topic"][0] == {"msg": "hello"}

    def test_emit_triggers_subscriber(self):
        bus = MetricsBus()
        received = []

        def listener(data):
            received.append(data)

        bus.subscribe("test_topic", listener)
        bus.emit("test_topic", {"value": 42})
        assert len(received) == 1
        assert received[0] == {"value": 42}

    def test_emit_multiple_subscribers(self):
        bus = MetricsBus()
        results = {"a": [], "b": []}

        def listener_a(data):
            results["a"].append(data)

        def listener_b(data):
            results["b"].append(data)

        bus.subscribe("test_topic", listener_a)
        bus.subscribe("test_topic", listener_b)
        bus.emit("test_topic", "x")
        assert results["a"] == ["x"]
        assert results["b"] == ["x"]

    def test_subscriber_not_called_for_other_topic(self):
        bus = MetricsBus()
        received = []
        bus.subscribe("topic_a", lambda d: received.append(d))
        bus.emit("topic_b", "data")
        assert received == []

    def test_error_isolation(self):
        """一个 listener 抛异常不应影响其他 listener"""
        bus = MetricsBus()
        received = []

        def broken_listener(data):
            raise ValueError("oops")

        def good_listener(data):
            received.append(data)

        bus.subscribe("test_topic", broken_listener)
        bus.subscribe("test_topic", good_listener)
        # 不应抛出异常
        bus.emit("test_topic", "data")
        assert received == ["data"]

    def test_emit_sync_works(self):
        bus = MetricsBus()
        received = []
        bus.subscribe("sync_topic", lambda d: received.append(d))
        bus.emit_sync("sync_topic", {"ok": True})
        assert received == [{"ok": True}]
        assert bus.data_store["sync_topic"] == [{"ok": True}]

    def test_emit_sync_error_isolation(self):
        bus = MetricsBus()
        received = []

        def bad(d):
            raise RuntimeError("bad")

        def good(d):
            received.append(d)

        bus.subscribe("t", bad)
        bus.subscribe("t", good)
        bus.emit_sync("t", "x")
        assert received == ["x"]

    @pytest.mark.asyncio
    async def test_emit_async_awaits_coro(self):
        bus = MetricsBus()
        results = []

        async def async_listener(data):
            results.append(data)

        bus.subscribe("async_topic", async_listener)
        await bus.emit_async("async_topic", "coro_data")
        assert results == ["coro_data"]

    @pytest.mark.asyncio
    async def test_emit_async_with_sync_listener(self):
        bus = MetricsBus()
        results = []

        def sync_listener(data):
            results.append(data)

        bus.subscribe("mixed", sync_listener)
        await bus.emit_async("mixed", "sync_ok")
        assert results == ["sync_ok"]

    @pytest.mark.asyncio
    async def test_emit_async_error_isolation(self):
        bus = MetricsBus()
        results = []

        async def bad(data):
            raise ValueError("async bad")

        def good(data):
            results.append(data)

        bus.subscribe("t", bad)
        bus.subscribe("t", good)
        await bus.emit_async("t", "data")
        assert results == ["data"]

    def test_data_store_separate_per_topic(self):
        bus = MetricsBus()
        bus.emit("a", 1)
        bus.emit("b", 2)
        bus.emit("a", 3)
        assert bus.data_store["a"] == [1, 3]
        assert bus.data_store["b"] == [2]

    def test_global_singleton_exists(self):
        from runtime.metrics.metrics_bus import metrics_bus

        assert hasattr(metrics_bus, "emit")
        assert hasattr(metrics_bus, "emit_sync")
        assert hasattr(metrics_bus, "emit_async")
        assert hasattr(metrics_bus, "subscribe")
