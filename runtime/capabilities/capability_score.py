"""Scores how well an agent's capabilities match a task's requirements."""

from typing import Any


class CapabilityScore:
    """Computes a match score between task required capabilities and agent capabilities."""

    def score(self, task: Any, capabilities: list[Any]) -> float:

        required = getattr(task, "required_capabilities", [])

        total = 0

        for r in required:

            for c in capabilities:

                if c.name == r:
                    total += c.score

        return total
