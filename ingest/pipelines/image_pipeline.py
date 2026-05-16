# ~/taichu/ingest/pipelines/image_pipeline.py
from pathlib import Path


def run(file_path: Path, target_dir: Path) -> Path:
    """图片 → Vision API 分析 → Markdown"""
    target = target_dir / (file_path.stem + ".md")

    import sys

    sys.path.insert(0, str(Path.home() / "taichu" / "tools" / "core"))
    from ingest.image_ingest import ingest_image

    result = ingest_image(file_path)
    target.write_text(
        f"# {file_path.stem}\n\n来源: {file_path.name}\n\n{result.text}",
        encoding="utf-8",
    )
    return target
