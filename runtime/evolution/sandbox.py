"""沙盒运行时，在隔离环境中评估 genome 表现。"""

# runtime/evolution/sandbox.py

import asyncio
from copy import deepcopy
from typing import Any


class SandboxRuntime:
    """沙盒运行时 — engine.py 依赖的类，包装 run_sandbox 函数"""

    def __init__(self, runtime_graph: Any, genome: Any, agents: Any = None) -> None:
        self.runtime_graph = runtime_graph
        self.genome = genome
        self._agents = agents or []

    async def run_test(self) -> dict[str, Any]:

        return await run_sandbox(self.genome, agents=self._agents, gbrain_output=None)


async def run_sandbox(genome: Any, agents: Any, gbrain_output: Any) -> dict[str, Any]:
    """运行 3 个 tick 的沙盒模拟，汇总所有 agent 的平均 latency/coherence/memory_hit。"""
    sandbox_agents = deepcopy(agents)

    for tick in range(3):

        await asyncio.gather(*[agent.tick() for agent in sandbox_agents])

        if gbrain_output:

            _ = gbrain_output[1]
            _ = gbrain_output[2]

    latency = sum(getattr(a, "avg_latency", lambda: 0.1)() for a in sandbox_agents) / max(len(sandbox_agents), 1)

    coherence = sum(getattr(a, "coherence", lambda: 0.5)() for a in sandbox_agents) / max(len(sandbox_agents), 1)

    memory_hit = sum(getattr(a, "memory_hit_rate", lambda: 0.5)() for a in sandbox_agents) / max(len(sandbox_agents), 1)

    metrics = {
        "latency": latency,
        "coherence": coherence,
        "memory_hit": memory_hit,
        "genome": genome,
    }

    return metrics
