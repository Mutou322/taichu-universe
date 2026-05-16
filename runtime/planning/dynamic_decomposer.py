# runtime/planning/dynamic_decomposer.py

from runtime.planning.workflow_graph import WorkflowGraph, WorkflowNode


class DynamicTaskDecomposer:

    def decompose(self, query):

        graph = WorkflowGraph()

        retrieval = WorkflowNode(
            task_type="retrieval",
            payload={
                "query": query,
            },
        )

        retrieval.required_capabilities = ["retrieval"]

        graph.add_node(retrieval)

        if "why" in query.lower() or "analyze" in query.lower():

            analysis = WorkflowNode(
                task_type="graph_analysis",
                payload={
                    "query": query,
                },
                dependencies=[
                    retrieval.node_id,
                ],
            )

            analysis.required_capabilities = ["graph_analysis"]

            graph.add_node(analysis)

        if "remember" in query.lower() or "memory" in query.lower():

            memory = WorkflowNode(
                task_type="memory",
                payload={
                    "query": query,
                },
                dependencies=[
                    retrieval.node_id,
                ],
            )

            memory.required_capabilities = ["memory"]

            graph.add_node(memory)

        synthesis = WorkflowNode(
            task_type="synthesis",
            payload={
                "query": query,
            },
        )

        synthesis.required_capabilities = ["synthesis"]

        synthesis.dependencies = [n.node_id for n in graph.nodes.values() if n.task_type != "synthesis"]

        graph.add_node(synthesis)

        return graph
