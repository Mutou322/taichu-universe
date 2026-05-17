"""PDF/Office 文档 Ingestion — 通过 markitdown 转换为 Markdown"""

from pathlib import Path

from markitdown import MarkItDown

from .types import IngestResult

md = MarkItDown()


def ingest_pdf(path: Path) -> IngestResult:
    """将 PDF/Office 文档转换为结构化文本"""
    try:
        result = md.convert(str(path))
        text = result.text_content if result and result.text_content else ""
    except Exception as e:
        text = f"[转换失败: {e}]"

    return IngestResult(
        text=text,
        modality="pdf" if path.suffix.lower() == ".pdf" else "office",
        metadata={
            "source": str(path),
            "type": path.suffix.lower().lstrip("."),
        },
    )
