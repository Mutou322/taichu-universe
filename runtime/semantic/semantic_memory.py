# runtime/semantic/semantic_memory.py

import time


class SemanticMemory:

    def __init__(self):
        self.nodes = {}

    def activate(self, concept, strength=1.0, source=None):
        if concept not in self.nodes:
            self.nodes[concept] = {
                "activation": 0.0,
                "sources": set(),
                "last_update": time.time(),
            }

        node = self.nodes[concept]
        node["activation"] += strength
        if source:
            node["sources"].add(source)
        node["last_update"] = time.time()

    def get_activation(self, concept):
        if concept not in self.nodes:
            return 0.0
        return self.nodes[concept]["activation"]

    def snapshot(self):
        return self.nodes
