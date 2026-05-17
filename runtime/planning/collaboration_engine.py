"""多 Agent 协作结果合并引擎。"""

# runtime/planning/collaboration_engine.py

from typing import Any


class CollaborationEngine:
    """合并多个 agent 在同一 workflow 中的执行结果。"""

    def merge_results(self, workspace: Any, workflow_id: str) -> str:

        results = workspace.read_workflow(workflow_id)

        merged = []

        for node_id, value in results.items():

            merged.append(value)

        return "\n".join(merged)
