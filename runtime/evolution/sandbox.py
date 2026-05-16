# runtime/evolution/sandbox.py

import asyncio
from copy import deepcopy


class SandboxRuntime:
    """沙盒运行时 — engine.py 依赖的类，包装 run_sandbox 函数"""

    def __init__(self, runtime_graph, genome):
        self.runtime_graph = runtime_graph
        self.genome = genome

    async def run_test(self):
        """执行沙盒实验，返回评估指标"""
        from runtime.evolution.mutation import GenomeMutator
        from runtime.metrics.metrics_bus import metrics_bus

        mutator = GenomeMutator()
        mutated = mutator.mutate(self.genome)

        # 用变异后的 genome 跑一轮沙盒
        return await run_sandbox(mutated, agents=[], gbrain_output=None)


async def run_sandbox(genome, agents, gbrain_output):

    sandbox_agents = deepcopy(agents)

    for tick in range(3):

        await asyncio.gather(*[agent.tick() for agent in sandbox_agents])

        if gbrain_output:

            clusters = gbrain_output[1]
            gravity = gbrain_output[2]

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
