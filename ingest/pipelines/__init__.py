# ~/taichu/ingest/pipelines/__init__.py
import hashlib
import shutil
from pathlib import Path

from . import image_pipeline, markdown_pipeline, pdf_pipeline

try:
    from . import compress_pipeline
except ImportError:
    compress_pipeline = None

SUPPORTED = {
    # 纯文本 / 源码（直接走 markdown 管道，不做 LLM 编译）
    ".md": markdown_pipeline.run,
    ".txt": markdown_pipeline.run,
    ".json": markdown_pipeline.run,
    ".csv": markdown_pipeline.run,
    ".xml": markdown_pipeline.run,
    ".yaml": markdown_pipeline.run,
    ".toml": markdown_pipeline.run,
    ".py": markdown_pipeline.run,
    ".js": markdown_pipeline.run,
    ".ts": markdown_pipeline.run,
    ".rs": markdown_pipeline.run,
    ".c": markdown_pipeline.run,
    ".cpp": markdown_pipeline.run,
    ".h": markdown_pipeline.run,
    ".hpp": markdown_pipeline.run,
    ".java": markdown_pipeline.run,
    ".go": markdown_pipeline.run,
    ".rb": markdown_pipeline.run,
    ".sh": markdown_pipeline.run,
    ".bash": markdown_pipeline.run,
    # Office / 文档（pdf_pipeline 含 markitdown 转换）
    ".pdf": pdf_pipeline.run,
    ".doc": pdf_pipeline.run,
    ".docx": pdf_pipeline.run,
    ".ppt": pdf_pipeline.run,
    ".pptx": pdf_pipeline.run,
    ".xls": pdf_pipeline.run,
    ".xlsx": pdf_pipeline.run,
    ".html": pdf_pipeline.run,
    ".htm": pdf_pipeline.run,
    ".epub": pdf_pipeline.run,
    ".rtf": pdf_pipeline.run,
    # 图片（OCR → Markdown）
    ".png": image_pipeline.run,
    ".jpg": image_pipeline.run,
    ".jpeg": image_pipeline.run,
    ".webp": image_pipeline.run,
    ".gif": image_pipeline.run,
    ".bmp": image_pipeline.run,
    ".svg": image_pipeline.run,
    # 压缩包（解压后递归处理内部文件）
    ".zip": compress_pipeline and compress_pipeline.run,
    ".tar": compress_pipeline and compress_pipeline.run,
    ".gz": compress_pipeline and compress_pipeline.run,
    ".bz2": compress_pipeline and compress_pipeline.run,
    ".7z": compress_pipeline and compress_pipeline.run,
    ".rar": compress_pipeline and compress_pipeline.run,
    # WebAssembly（记录元信息，无转换）
    ".wasm": markdown_pipeline.run,
}

# 可上传文件类型（前端可据此过滤）
UPLOAD_EXTENSIONS = sorted(SUPPORTED.keys(), key=lambda x: (len(x), x))


def file_hash(file_path: Path, length: int = 16) -> str:
    """计算文件 SHA256 哈希"""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:length]


def store_file(source: Path, store_dir: Path) -> dict:
    """
    将文件存入统一存储目录，按哈希去重。
    返回 metadata: {hash, path, original_name, size}
    """
    store_dir = Path(store_dir)
    store_dir.mkdir(parents=True, exist_ok=True)

    h = file_hash(source)
    original = source.name
    target = store_dir / f"{h}_{original}"

    if not target.exists():
        shutil.copy2(source, target)

    return {
        "hash": h,
        "path": str(target),
        "original_name": original,
        "size": target.stat().st_size,
    }


def dispatch(file_path: Path, target_dir: Path, store_dir: Path = None) -> dict:
    """
    调度文件到对应管道处理。

    参数:
        file_path: 源文件路径
        target_dir: 管道处理后输出目录
        store_dir: 统一文件存储目录（可选），传入则先做哈希去重

    返回:
        {"ok": bool, "pipeline": str, "stored": dict|None, "result": Path|None, "error": str}
    """
    ext = file_path.suffix.lower()
    pipeline = SUPPORTED.get(ext)
    if pipeline is None:
        return {"ok": False, "error": f"不支持的文件格式: {ext}"}

    # 先做哈希去重存储
    stored = None
    if store_dir:
        stored = store_file(file_path, store_dir)

    try:
        result = pipeline(file_path, target_dir)
        return {
            "ok": True,
            "pipeline": pipeline.__module__,
            "stored": stored,
            "result": str(result),
        }
    except Exception as e:
        return {
            "ok": False,
            "pipeline": pipeline.__module__,
            "stored": stored,
            "error": str(e),
        }
