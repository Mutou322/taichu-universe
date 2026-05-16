import time
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class MetricEvent:
    name: str
    value: float
    tags: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
