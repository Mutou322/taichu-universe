# runtime/specialization/specialization_metrics.py

from runtime.metrics.metrics_bus import metrics_bus
from runtime.metrics.models import MetricEvent


async def emit_specialization_metrics(agents):

    for agent in agents:

        profile = agent.profile

        await metrics_bus.emit_async(
            MetricEvent(
                name="agent_specialization",
                value=profile.expertise_score,
                tags={
                    "agent": agent.agent_id,
                    "domain": profile.primary_domain,
                    "stage": profile.evolution_stage,
                },
            )
        )
