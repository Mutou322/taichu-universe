"""任务优先级引擎，按任务类型分配优先级。"""

# runtime/scheduler/task_priority.py

from typing import Any


class TaskPriorityEngine:
    """根据任务类型计算优先级：retrieval=2, planning=3, evolution=4, 其他=1。"""

    def compute_priority(self, task: Any) -> int:
        """retrieval +1, planning +2, evolution +3，返回优先级整数。"""
        base = 1

        if task.task_type == "retrieval":
            base += 1

        if task.task_type == "planning":
            base += 2

        if task.task_type == "evolution":
            base += 3

        return base
