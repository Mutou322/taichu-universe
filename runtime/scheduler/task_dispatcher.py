"""任务派发器，委托 matcher 选择 agent。"""

# runtime/scheduler/task_dispatcher.py

from typing import Any


class TaskDispatcher:
    """将任务派发给 matcher 选中的 agent。"""

    def __init__(self, matcher: Any) -> None:

        self.matcher = matcher

    def dispatch(self, task: Any, agents: Any) -> Any:

        return self.matcher.select_agent(task, agents)
