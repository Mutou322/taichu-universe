"""静态任务分解器，生成固定的检索-分析-记忆-合成工作流。"""

# runtime/planning/task_decomposer.py

from runtime.planning.workflow_graph import WorkflowGraph, WorkflowNode


class TaskDecomposer:
    """将用户查询分解为 retrieval -> graph_analysis/memory -> synthesis 的 DAG。"""

    def decompose(self, user_query: str) -> WorkflowGraph:

        graph = WorkflowGraph()

        retrieval = WorkflowNode(
            task_type="retrieval",
            payload={
                "query": user_query,
                "concepts": ["Transformer", "Attention"],
            },
        )

        graph_analysis = WorkflowNode(
            task_type="graph_analysis",
            payload={
                "query": user_query,
                "concepts": ["LLM", "Graph", "Planning"],
            },
            dependencies=[
                retrieval.node_id,
            ],
        )

        memory = WorkflowNode(
            task_type="memory",
            payload={
                "query": user_query,
                "concepts": ["Memory", "Semantic"],
            },
            dependencies=[
                retrieval.node_id,
            ],
        )

        synthesis = WorkflowNode(
            task_type="synthesis",
            payload={
                "query": user_query,
                "concepts": ["LLM", "Synthesis", "Planning"],
            },
            dependencies=[
                graph_analysis.node_id,
                memory.node_id,
            ],
        )

        for n in [
            retrieval,
            graph_analysis,
            memory,
            synthesis,
        ]:
            graph.add_node(n)

        return graph
