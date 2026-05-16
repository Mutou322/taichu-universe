# runtime/gbrain/gravity_scheduler.py

import asyncio

from runtime.gbrain.gravity_metrics import emit_gravity_metrics
from runtime.gbrain.semantic_gravity import SemanticGravity as SemanticGravityEngine


class GravityScheduler:

    def __init__(self, graph):
        self.graph = graph
        self.engine = SemanticGravityEngine()
        self.running = False

    async def start(self):
        self.running = True
        while self.running:
            gravity_updates = self.engine.tick(self.graph.nodes)
            await emit_gravity_metrics(gravity_updates)
            await asyncio.sleep(5)

    def stop(self):
        self.running = False
