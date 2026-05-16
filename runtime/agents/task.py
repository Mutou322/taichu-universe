# runtime/agents/task.py

import time
import uuid
from dataclasses import dataclass, field


@dataclass
class RuntimeTask:
    task_type: str
    payload: dict

    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)
    priority: int = 1
