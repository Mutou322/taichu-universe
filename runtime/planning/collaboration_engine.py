# runtime/planning/collaboration_engine.py


class CollaborationEngine:

    def merge_results(self, workspace, workflow_id):

        results = workspace.read_workflow(workflow_id)

        merged = []

        for node_id, value in results.items():

            merged.append(value)

        return "\n".join(merged)
