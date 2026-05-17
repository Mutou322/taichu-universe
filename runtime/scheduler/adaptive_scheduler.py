"""自适应调度器，从 agent 池收集就绪任务并按优先级排序。"""

# runtime/scheduler/adaptive_scheduler.py

from typing import Any


class AdaptiveScheduler:
    """从所有 agent 收集就绪任务，按优先级降序排列。"""

    def __init__(self, agents: Any) -> None:

        self.agents = agents

    def get_ready_nodes(self) -> list[Any]:

        ready = []

        for agent in self.agents:

            if hasattr(agent, "get_ready_tasks"):
                ready.extend(agent.get_ready_tasks())

        ready.sort(key=lambda t: getattr(t, "priority", 0), reverse=True)

        return ready

    async def dispatch(self, agent: Any, node: Any) -> tuple[bool, float]:

        return True, 0.0
