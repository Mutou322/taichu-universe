"""Graph analysis agent specialization."""

import asyncio
import logging

from runtime.agents.base_agent import BaseAgent
from runtime.specialization.specialization_profile import SpecializationProfile

logger = logging.getLogger(__name__)


class GraphAgent(BaseAgent):
    """Agent specialized in graph analysis tasks."""

    def __init__(self, agent_id: str | None = None) -> None:

        super().__init__(agent_id)

        self.profile = SpecializationProfile(
            primary_domain="GraphAnalysis",
        )

    async def tick(self) -> None:

        if self.current_task:

            logger.info("[GraphAgent] %s", self.current_task.payload)

            await asyncio.sleep(0.5)

            self.current_task = None

            self.load = max(0, self.load - 1)
