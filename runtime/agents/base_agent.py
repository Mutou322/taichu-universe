# runtime/agents/base_agent.py

import asyncio
import uuid
from abc import ABC, abstractmethod


class BaseAgent(ABC):

    def __init__(self, agent_id=None):

        if agent_id is None:
            agent_id = f"{self.__class__.__name__}_{uuid.uuid4().hex[:8]}"

        self.agent_id = agent_id
        self.running = False
        self.current_task = None
        self.load = 0
        self.genome = None

    def attention_vector(self):
        if hasattr(self, "profile") and hasattr(self.profile, "semantic_affinity"):
            return dict(self.profile.semantic_affinity)
        return {}

    def adapt_attention(self, ecosystem, node, reward):

        if not hasattr(self, "profile") or not hasattr(node, "task_type"):
            return

        lr = 0.1

        old_val = self.profile.semantic_affinity.get(node.task_type, 0.5)

        new_val = max(0.0, min(5.0, old_val + lr * reward))

        self.profile.semantic_affinity[node.task_type] = new_val

        if hasattr(self, "genome") and self.genome is not None:
            self.genome.adjust(node.task_type, reward)

    def update_genome(self, genome):
        self.genome = genome

    async def start(self):
        self.running = True
        while self.running:
            await asyncio.sleep(0.1)
            await self.tick()

    async def stop(self):
        self.running = False

    @abstractmethod
    async def tick(self):
        pass
