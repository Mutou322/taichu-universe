"""持续工作流执行器，驱动主循环 tick 和进化触发。"""

# runtime/planning/workflow_executor.py

import asyncio
from typing import Any


class ContinuousWorkflowExecutor:
    """每个 tick 获取就绪节点、派发执行、更新生态系统并定期触发进化。"""

    def __init__(self, scheduler: Any, ecosystem: Any, evolution_engine: Any, metrics_bus: Any) -> None:

        self.scheduler = scheduler
        self.ecosystem = ecosystem
        self.evolution_engine = evolution_engine
        self.metrics_bus = metrics_bus
        self.tick = 0

    async def run_tick(self) -> None:
        """执行一个主循环 tick：派发就绪节点、更新生态、每 5 tick 触发进化。"""
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

    async def execute_node(self, node: Any) -> None:
        """选择 agent 执行节点，根据成功/失败给予注意力度奖励或惩罚。"""
        agent = self.ecosystem.select_agent(node)

        success, latency = await self.scheduler.dispatch(agent, node)

        reward = 1.0 if success else -1.0

        agent.adapt_attention(self.ecosystem, node, reward)
