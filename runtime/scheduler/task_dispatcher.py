# runtime/scheduler/task_dispatcher.py


class TaskDispatcher:

    def __init__(self, matcher):

        self.matcher = matcher

    def dispatch(self, task, agents):

        return self.matcher.select_agent(task, agents)
