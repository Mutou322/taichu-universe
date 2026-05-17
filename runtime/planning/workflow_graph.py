"""工作流 DAG 图数据结构：节点与图。"""

# runtime/planning/workflow_graph.py

import uuid
from dataclasses import dataclass, field


@dataclass
class WorkflowNode:
    """工作流节点，含任务类型、负载、依赖和所需能力。"""

    task_type: str

    payload: dict

    node_id: str = field(
        default_factory=lambda: str(uuid.uuid4()),
    )

    dependencies: list = field(
        default_factory=list,
    )

    required_capabilities: list = field(
        default_factory=list,
    )

    completed: bool = False


class WorkflowGraph:
    """工作流 DAG，管理节点增删和依赖就绪判断。"""

    def __init__(self) -> None:

        self.nodes: dict[str, WorkflowNode] = {}

    def add_node(self, node: WorkflowNode) -> None:

        self.nodes[node.node_id] = node

    def ready_nodes(self) -> list[WorkflowNode]:

        ready = []

        for node in self.nodes.values():

            if node.completed:
                continue

            deps_done = all(self.nodes[d].completed for d in node.dependencies)

            if deps_done:
                ready.append(node)

        return ready

    def mark_completed(self, node_id: str) -> None:

        self.nodes[node_id].completed = True
