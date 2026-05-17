"""Detects emergent focus hotspots above a threshold."""

from typing import Any


class EmergentFocus:
    """Identifies attention hotspots where the attention value exceeds a threshold."""

    def detect(self, field: Any, threshold: float = 3.0) -> list[tuple[str, float]]:

        focus = []

        for node_id, value in field.node_attention.items():

            if value >= threshold:

                focus.append((node_id, value))

        return sorted(
            focus,
            key=lambda x: x[1],
            reverse=True,
        )
