# runtime/planning/workflow_graph.py

import uuid
from dataclasses import dataclass, field


@dataclass
class WorkflowNode:

    task_type: str

    payload: dict

    node_id: str = field(
        default_factory=lambda: str(uuid.uuid4()),
    )

    dependencies: list = field(
        default_factory=list,
    )

    completed: bool = False


class WorkflowGraph:

    def __init__(self):

        self.nodes = {}

    def add_node(self, node):

        self.nodes[node.node_id] = node

    def ready_nodes(self):

        ready = []

        for node in self.nodes.values():

            if node.completed:
                continue

            deps_done = all(self.nodes[d].completed for d in node.dependencies)

            if deps_done:
                ready.append(node)

        return ready

    def mark_completed(self, node_id):

        self.nodes[node_id].completed = True
