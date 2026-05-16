# runtime/planning/workflow_executor.py

import asyncio


class ContinuousWorkflowExecutor:

    def __init__(self, scheduler, ecosystem, evolution_engine, metrics_bus):

        self.scheduler = scheduler
        self.ecosystem = ecosystem
        self.evolution_engine = evolution_engine
        self.metrics_bus = metrics_bus
        self.tick = 0

    async def run_tick(self):

        ready_nodes = self.scheduler.get_ready_nodes()

        await asyncio.gather(*[self.execute_node(node) for node in ready_nodes])

        await self.ecosystem.update(self.scheduler.agents)

        self.metrics_bus.emit(
            "attention_map",
            self.ecosystem.attention_field.node_attention,
        )

        if self.tick % 5 == 0:

            gbrain_nodes = {a.agent_id: getattr(a, "profile", None) for a in self.scheduler.agents}

            gbrain_output = (
                self.ecosystem.gbrain.analyze(
                    gbrain_nodes,
                )
                if hasattr(self.ecosystem, "gbrain")
                else None
            )

            await self.evolution_engine.run_generation(
                self.scheduler.agents,
                gbrain_output,
            )

        self.tick += 1

    async def execute_node(self, node):

        agent = self.ecosystem.select_agent(node)

        success, latency = await self.scheduler.dispatch(agent, node)

        reward = 1.0 if success else -1.0

        agent.adapt_attention(self.ecosystem, node, reward)
