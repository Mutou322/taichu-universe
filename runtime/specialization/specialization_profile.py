"""Specialization profile dataclass for agent expertise state."""

from dataclasses import dataclass, field


@dataclass
class SpecializationProfile:
    """Dataclass tracking agent specialization: domain, expertise, affinity, and evolution stage."""

    primary_domain: str

    expertise_score: float = 1.0

    semantic_affinity: dict = field(default_factory=dict)

    completed_tasks: int = 0

    evolution_stage: int = 1
