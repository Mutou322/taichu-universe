# runtime/agents/planner_agent.py

import asyncio

from runtime.agents.base_agent import BaseAgent
from runtime.specialization.specialization_profile import SpecializationProfile


class PlannerAgent(BaseAgent):

    def __init__(self, agent_id=None, activation_engine=None):

        super().__init__(agent_id)

        self.activation_engine = activation_engine

        self.profile = SpecializationProfile(
            primary_domain="LLM",
        )

    async def tick(self):

        if self.current_task:

            if self.activation_engine:
                self.activation_engine.process_task(
                    self.agent_id,
                    self.current_task,
                )

            print(
                f"[{self.agent_id}] planning:",
                self.current_task.payload,
            )

            await asyncio.sleep(1.0)

            self.current_task = None

            self.load = max(0, self.load - 1)
