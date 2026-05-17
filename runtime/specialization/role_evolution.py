"""Evolves agent role based on expertise milestones."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class RoleEvolutionEngine:
    """Promotes agents through evolution stages based on accumulated expertise."""

    def evolve(self, agent: Any) -> None:

        if not hasattr(agent, "profile"):
            return

        profile = agent.profile

        if profile.expertise_score > 5 and profile.evolution_stage == 1:

            profile.evolution_stage = 2

            logger.info("[Evolution] %s -> Specialist", agent.agent_id)

        elif profile.expertise_score > 10 and profile.evolution_stage == 2:

            profile.evolution_stage = 3

            logger.info("[Evolution] %s -> Expert", agent.agent_id)
