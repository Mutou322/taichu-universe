from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class IngestResult:
    text: str
    modality: str
    metadata: Dict[str, Any]
