# runtime/agents/agent_factory.py

from runtime.agents.graph_agent import GraphAgent
from runtime.agents.memory_agent import MemoryAgent
from runtime.agents.synthesizer_agent import SynthesizerAgent


class AgentFactory:

    def create(self, role):

        if role == "graph_analysis":
            return GraphAgent()

        if role == "memory":
            return MemoryAgent()

        if role == "synthesis":
            return SynthesizerAgent()

        raise ValueError(f"Unknown role: {role}")
