# runtime/planning/planning_metrics.py

from runtime.metrics.metrics_bus import metrics_bus
from runtime.metrics.models import MetricEvent


async def emit_workflow_metrics(workflow):

    total_nodes = len(workflow.nodes)

    completed = sum(1 for n in workflow.nodes.values() if n.completed)

    await metrics_bus.emit_async(
        MetricEvent(
            name="workflow_progress",
            value=completed,
            tags={
                "total_nodes": total_nodes,
            },
        )
    )
