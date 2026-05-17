"""基于 asyncio.Queue 的异步任务队列封装。"""

# runtime/scheduler/runtime_queue.py

import asyncio
from typing import Any


class RuntimeQueue:
    """异步任务队列，封装 asyncio.Queue 的 put/get/qsize。"""

    def __init__(self) -> None:

        self._queue: asyncio.Queue = asyncio.Queue()

    async def put(self, item: Any) -> None:

        await self._queue.put(item)

    async def get(self) -> Any:

        return await self._queue.get()

    def qsize(self) -> int:

        return self._queue.qsize()
