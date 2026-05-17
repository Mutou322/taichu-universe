"""负载均衡器，选择当前负载最低的 agent。"""

# runtime/scheduler/load_balancer.py

from typing import Any


class LoadBalancer:
    """从 agent 列表中选取 load 最小的 agent。"""

    def select_agent(self, agents: list[Any]) -> Any:
        if not agents:
            return None

        agents = sorted(agents, key=lambda a: getattr(a, "load", 0))
        return agents[0]
