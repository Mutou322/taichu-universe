"""Stores snapshots of attention maps for historical analysis."""

import copy
from collections import deque
from typing import Any


class AttentionHistory:
    """Bounded history buffer that stores deep copies of attention map weights."""

    def __init__(self, maxlen: int = 20) -> None:

        self.history: deque[Any] = deque(maxlen=maxlen)

    def add_snapshot(self, attention_map: Any) -> None:

        self.history.append(copy.deepcopy(attention_map.all_weights()))

    def get_history(self) -> list[Any]:

        return list(self.history)
