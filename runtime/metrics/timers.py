import time
from contextlib import contextmanager

from .metrics_bus import metrics_bus
from .models import MetricEvent


@contextmanager
def metric_timer(name: str, **tags):
    start = time.perf_counter()

    try:
        yield
    finally:
        duration = (time.perf_counter() - start) * 1000

        event = MetricEvent(name=name, value=duration, tags=tags)

        # 尝试异步 emit，没有事件循环时用 print 兜底
        try:
            import asyncio

            loop = asyncio.get_running_loop()
            if loop and loop.is_running():
                asyncio.create_task(metrics_bus.emit_async(event.name, event))
                return
        except RuntimeError:
            pass

        # 同步 fallback（用 emit_sync 而非 asyncio.run）
        try:
            metrics_bus.emit_sync(event.name, event)
        except Exception:
            pass
