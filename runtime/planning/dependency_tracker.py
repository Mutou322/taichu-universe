"""工作流依赖追踪器，识别就绪节点。"""

# runtime/planning/dependency_tracker.py

from typing import Any


class DependencyTracker:
    """检查工作流图中所有依赖已满足的就绪节点。"""

    def ready(self, workflow: Any) -> list[Any]:

        return workflow.ready_nodes()
