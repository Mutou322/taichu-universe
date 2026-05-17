"""Retrieval agent for transformer-based knowledge retrieval."""

import asyncio
import logging
from typing import Any

from runtime.agents.base_agent import BaseAgent
from runtime.specialization.specialization_profile import SpecializationProfile

logger = logging.getLogger(__name__)


class RetrievalAgent(BaseAgent):
    """Agent specialized in retrieval tasks with optional activation engine."""

    def __init__(self, agent_id: str | None = None, activation_engine: Any = None) -> None:

        super().__init__(agent_id)

        self.activation_engine = activation_engine

        self.profile = SpecializationProfile(
            primary_domain="Transformer",
        )

    async def tick(self) -> None:

        if self.current_task:

            if self.activation_engine:
                self.activation_engine.process_task(
                    self.agent_id,
                    self.current_task,
                )

            logger.info("[%s] retrieval: %s", self.agent_id, self.current_task.payload)

            await asyncio.sleep(0.5)

            self.current_task = None

            self.load = max(0, self.load - 1)
