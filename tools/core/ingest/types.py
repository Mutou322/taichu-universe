from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class IngestResult:
    text: str
    modality: str
    metadata: Dict[str, Any]
