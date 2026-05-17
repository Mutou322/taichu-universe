"""Cooperative attention bonus for multi-agent reinforcement."""

from typing import Any


class CooperativeAttention:
    """Computes cooperation bonus when multiple agents attend to the same node."""

    def reinforce(self, field: Any, node_id: str, agents: list[Any]) -> float:

        total = 0.0

        for agent in agents:

            total += field.get_agent_attention(
                agent.agent_id,
                node_id,
            )

        cooperation_bonus = total * 0.2

        field.node_attention[node_id] += cooperation_bonus

        return cooperation_bonus
