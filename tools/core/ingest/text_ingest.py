from pathlib import Path

from .types import IngestResult


def ingest_text(path: Path) -> IngestResult:
    content = path.read_text(encoding="utf-8", errors="replace")

    return IngestResult(
        text=content,
        modality="text",
        metadata={
            "source": str(path),
            "type": "text",
            "ext": path.suffix.lower(),
        },
    )
