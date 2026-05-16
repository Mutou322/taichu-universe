# ~/taichu/ingest/pipelines/markdown_pipeline.py
import shutil
from pathlib import Path


def run(file_path: Path, target_dir: Path) -> Path:
    """纯 Markdown 文件直接复制到 wiki 的 raw 预处理区，返回处理后路径"""
    target = target_dir / file_path.name
    shutil.copy2(file_path, target)
    return target
