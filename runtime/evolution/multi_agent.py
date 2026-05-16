# runtime/evolution/multi_agent.py

import asyncio

from runtime.evolution.engine import EvolutionEngine


class MultiAgentEvolution:

    def __init__(self, runtime_graph, agents_genomes):
        """
        agents_genomes: dict { agent_id: Genome }
        """
        self.runtime_graph = runtime_graph
        self.agents_genomes = agents_genomes

    async def run(self):
        """多 Agent 并行演化，每个 Agent 的 genome 独立"""
        tasks = []
        for agent_id, genome in self.agents_genomes.items():
            engine = EvolutionEngine(self.runtime_graph, genome)
            tasks.append(asyncio.create_task(engine.run_parallel_generation(generation_size=4)))

        results = await asyncio.gather(*tasks)

        # 更新每个 agent 的 base genome
        for i, agent_id in enumerate(self.agents_genomes.keys()):
            self.agents_genomes[agent_id] = results[i][1]["genome"]

        return self.agents_genomes
