# runtime/semantic/semantic_activation.py


class SemanticActivationEngine:

    def __init__(self, memory):
        self.memory = memory

    def process_task(self, agent_id, task):
        concepts = task.payload.get("concepts", [])
        for c in concepts:
            self.memory.activate(concept=c, strength=1.0, source=agent_id)
