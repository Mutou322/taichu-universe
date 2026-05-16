# runtime/planning/shared_workspace.py


class SharedWorkspace:

    def __init__(self):

        self.workspace = {}

    def write(self, workflow_id, node_id, value):

        if workflow_id not in self.workspace:
            self.workspace[workflow_id] = {}

        self.workspace[workflow_id][node_id] = value

    def read_workflow(self, workflow_id):

        return self.workspace.get(
            workflow_id,
            {},
        )
