# ~/taichu/ingest/pipelines/__init__.py
from pathlib import Path
from . import markdown_pipeline, pdf_pipeline, image_pipeline

SUPPORTED = {
    ".md": markdown_pipeline.run,
    ".pdf": pdf_pipeline.run,
    ".docx": pdf_pipeline.run,
    ".pptx": pdf_pipeline.run,
    ".xlsx": pdf_pipeline.run,
    ".html": pdf_pipeline.run,
    ".htm": pdf_pipeline.run,
    ".epub": pdf_pipeline.run,
    ".rtf": pdf_pipeline.run,
    ".png": image_pipeline.run,
    ".jpg": image_pipeline.run,
    ".jpeg": image_pipeline.run,
    ".webp": image_pipeline.run,
    ".gif": image_pipeline.run,
    ".bmp": image_pipeline.run,
}

def dispatch(file_path: Path, target_dir: Path) -> Path:
    ext = file_path.suffix.lower()
    pipeline = SUPPORTED.get(ext)
    if pipeline is None:
        raise ValueError(f"不支持的文件格式: {ext}")
    return pipeline(file_path, target_dir)
