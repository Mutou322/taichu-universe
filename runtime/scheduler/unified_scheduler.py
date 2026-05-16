# runtime/scheduler/unified_scheduler.py

import asyncio
import time


class UnifiedScheduler:

    async def dispatch(self, agent, task):

        agent.current_task = task

        start = time.monotonic()

        try:
            await agent.tick()
            success = True
        except Exception as e:
            print(f"[Scheduler] agent {agent.agent_id} failed: {e}")
            success = False

        latency = time.monotonic() - start

        await asyncio.sleep(0)

        return success, latency
