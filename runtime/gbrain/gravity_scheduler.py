"""引力调度器 — 定时执行语义引力计算并推送指标"""

import asyncio

from runtime.gbrain.gravity_metrics import emit_gravity_metrics
from runtime.gbrain.semantic_gravity import SemanticGravity as SemanticGravityEngine


class GravityScheduler:
    """按固定间隔驱动 SemanticGravity.tick() 并上报指标"""

    TICK_INTERVAL = 5

    def __init__(self, graph) -> None:
        self.graph = graph
        self.engine = SemanticGravityEngine()
        self.running = False

    async def start(self) -> None:
        self.running = True
        while self.running:
            gravity_updates = self.engine.tick(self.graph.nodes)
            await emit_gravity_metrics(gravity_updates)
            await asyncio.sleep(self.TICK_INTERVAL)

    def stop(self) -> None:
        self.running = False
