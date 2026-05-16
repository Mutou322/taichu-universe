# runtime/scheduler/runtime_queue.py

import asyncio


class RuntimeQueue:

    def __init__(self):

        self._queue = asyncio.Queue()

    async def put(self, item):

        await self._queue.put(item)

    async def get(self):

        return await self._queue.get()

    def qsize(self):

        return self._queue.qsize()
