"""多 Agent 共享工作空间，按 workflow 隔离读写。"""

# runtime/planning/shared_workspace.py

from typing import Any


class SharedWorkspace:
    """提供按 workflow_id 和 node_id 隔离的键值存储。"""

    def __init__(self) -> None:

        self.workspace: dict[str, dict[str, Any]] = {}

    def write(self, workflow_id: str, node_id: str, value: Any) -> None:

        if workflow_id not in self.workspace:
            self.workspace[workflow_id] = {}

        self.workspace[workflow_id][node_id] = value

    def read_workflow(self, workflow_id: str) -> dict[str, Any]:

        return self.workspace.get(
            workflow_id,
            {},
        )
