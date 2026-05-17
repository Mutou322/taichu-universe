"""Agent factory for creating agents of different roles by name."""

from typing import Any

from runtime.agents.graph_agent import GraphAgent
from runtime.agents.memory_agent import MemoryAgent
from runtime.agents.synthesizer_agent import SynthesizerAgent


class AgentFactory:
    """Factory that creates agent instances by role name."""

    def create(self, role: str) -> Any:

        if role == "graph_analysis":
            return GraphAgent()

        if role == "memory":
            return MemoryAgent()

        if role == "synthesis":
            return SynthesizerAgent()

        raise ValueError(f"Unknown role: {role}")
