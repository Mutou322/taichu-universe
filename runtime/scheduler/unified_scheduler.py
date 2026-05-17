"""统一调度器，执行 agent 任务并测量延迟和成功率。"""

# runtime/scheduler/unified_scheduler.py

import asyncio
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class UnifiedScheduler:
    """驱动 agent 执行单个任务，捕获异常并返回 (success, latency) 元组。"""

    async def dispatch(self, agent: Any, task: Any) -> tuple[bool, float]:
        """让 agent 执行一个 tick，记录耗时，捕获异常并返回 (成功标志, 延迟秒数)。"""
        agent.current_task = task

        start = time.monotonic()

        try:
            await agent.tick()
            success = True
        except Exception as e:
            logger.warning("agent %s failed: %s", agent.agent_id, e)
            success = False

        latency = time.monotonic() - start

        await asyncio.sleep(0)

        return success, latency
