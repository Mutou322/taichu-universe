"""Priority-based asynchronous task queue."""

import asyncio
from typing import Any


class TaskQueue:
    """Priority queue for async task dispatching."""

    def __init__(self) -> None:
        self.queue: asyncio.PriorityQueue[tuple[int, str, Any]] = asyncio.PriorityQueue()

    async def put(self, task: Any) -> None:
        # 用 (priority, id) 做排序元组，避免比较 task 对象
        await self.queue.put((task.priority, task.task_id, task))

    async def get(self) -> Any:
        _, _, task = await self.queue.get()
        return task
