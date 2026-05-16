# runtime/agents/task_queue.py

import asyncio


class TaskQueue:

    def __init__(self):
        self.queue = asyncio.PriorityQueue()

    async def put(self, task):
        # 用 (priority, id) 做排序元组，避免比较 task 对象
        await self.queue.put((task.priority, task.task_id, task))

    async def get(self):
        _, _, task = await self.queue.get()
        return task
