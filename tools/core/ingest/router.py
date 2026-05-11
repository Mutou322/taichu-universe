from pathlib import Path

from .types import IngestResult
from .text_ingest import ingest_text
from .image_ingest import ingest_image
from .pdf_ingest import ingest_pdf

TEXT_EXT = {".md", ".txt", ".csv", ".json", ".xml"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".ico", ".svg", ".tiff", ".tif"}
PDF_EXT = {".pdf"}
OFFICE_EXT = {".docx", ".pptx", ".xlsx", ".html", ".htm", ".epub", ".rtf"}


def ingest_file(path: str | Path) -> IngestResult:
    path = Path(path)
    ext = path.suffix.lower()

    if ext in TEXT_EXT:
        return ingest_text(path)

    if ext in IMAGE_EXT:
        return ingest_image(path)

    if ext in PDF_EXT:
        return ingest_pdf(path)

    if ext in OFFICE_EXT:
        # Office 格式也走 markitdown
        return ingest_pdf(path)

    raise ValueError(f"不支持的文件类型: {ext}")
