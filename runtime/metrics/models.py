"""指标领域模型，定义事件和检索性能的数据结构"""

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MetricEvent:
    """通用指标事件，含名称、数值、标签和时间戳"""

    name: str
    value: float
    tags: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
