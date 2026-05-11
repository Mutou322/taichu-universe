# ~/taichu/ingest/pipelines/pdf_pipeline.py
from pathlib import Path
import subprocess
import sys

def run(file_path: Path, target_dir: Path) -> Path:
    """PDF → Markdown，优先使用 markitdown，降级用 pymupdf4llm"""
    target = target_dir / (file_path.stem + ".md")
    
    # 方式1：markitdown（支持 PDF/Word/PPT/HTML）
    try:
        from markitdown import MarkItDown
        md = MarkItDown()
        result = md.convert(str(file_path))
        target.write_text(result.text_content, encoding="utf-8")
        return target
    except ImportError:
        pass

    # 方式2：pymupdf4llm（原生 PDF 解析，含 OCR）
    try:
        import pymupdf4llm
        md_text = pymupdf4llm.to_markdown(str(file_path))
        target.write_text(md_text, encoding="utf-8")
        return target
    except ImportError:
        pass

    # 方式3：纯 PyMuPDF 提取文本
    try:
        import fitz
        doc = fitz.open(file_path)
        full_text = "\n\n".join([page.get_text() for page in doc])
        target.write_text(full_text, encoding="utf-8")
        return target
    except ImportError:
        raise RuntimeError("至少需要安装 markitdown 或 pymupdf 来处理 PDF")
