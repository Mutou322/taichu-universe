# runtime/agents/memory_agent.py

import asyncio

from runtime.agents.base_agent import BaseAgent
from runtime.specialization.specialization_profile import SpecializationProfile


class MemoryAgent(BaseAgent):

    def __init__(self, agent_id=None):

        super().__init__(agent_id)

        self.profile = SpecializationProfile(
            primary_domain="Memory",
        )

    async def tick(self):

        if self.current_task:

            print(
                "[MemoryAgent]",
                self.current_task.payload,
            )

            await asyncio.sleep(0.3)

            self.current_task = None

            self.load = max(0, self.load - 1)
