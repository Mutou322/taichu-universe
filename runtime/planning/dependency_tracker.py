# runtime/planning/dependency_tracker.py


class DependencyTracker:

    def ready(self, workflow):

        return workflow.ready_nodes()
