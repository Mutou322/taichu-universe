"""Applies exponential decay to attention values over time."""

from typing import Any


class AttentionDecay:
    """Decays all attention values in a field by the configured decay rate each tick."""

    def __init__(self, decay_rate: float = 0.95) -> None:

        self.decay_rate = decay_rate

    def tick(self, field: Any) -> None:

        for node_id in list(field.node_attention.keys()):

            field.node_attention[node_id] *= self.decay_rate
