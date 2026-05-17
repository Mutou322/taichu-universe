"""Task data model for runtime task representation."""

import time
import uuid
from dataclasses import dataclass, field


@dataclass
class RuntimeTask:
    """Dataclass representing a runtime task with type, payload, and metadata."""

    task_type: str
    payload: dict

    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)
    priority: int = 1
