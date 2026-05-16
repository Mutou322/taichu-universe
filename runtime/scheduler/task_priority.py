# runtime/scheduler/task_priority.py


class TaskPriorityEngine:

    def compute_priority(self, task):
        base = 1

        if task.task_type == "retrieval":
            base += 1

        if task.task_type == "planning":
            base += 2

        if task.task_type == "evolution":
            base += 3

        return base
