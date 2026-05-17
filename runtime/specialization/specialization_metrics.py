"""Emits specialization metrics for agent profiles."""

from typing import Any

from runtime.metrics.metrics_bus import metrics_bus
from runtime.metrics.models import MetricEvent


async def emit_specialization_metrics(agents: list[Any]) -> None:

    for agent in agents:

        if not hasattr(agent, "profile"):
            continue

        profile = agent.profile

        await metrics_bus.emit_async(
            "specialization",
            MetricEvent(
                name="agent_specialization",
                value=profile.expertise_score,
                tags={
                    "agent": agent.agent_id,
                    "domain": profile.primary_domain,
                    "stage": profile.evolution_stage,
                },
            ),
        )
