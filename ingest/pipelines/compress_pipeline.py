# ~/taichu/ingest/pipelines/compress_pipeline.py
"""压缩包解压管道：zip/tar/gz/7z/rar → 提取内部文件逐个处理"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def run(file_path: Path, target_dir: Path) -> Path:
    """解压压缩包到 target_dir 下的子目录，返回索引文件路径。"""
    stem = file_path.stem
    extract_dir = target_dir / stem
    extract_dir.mkdir(parents=True, exist_ok=True)

    ext = file_path.suffix.lower()
    ok = False

    if ext == ".zip":
        ok = _unzip(file_path, extract_dir)
    elif ext in (".tar", ".gz", ".bz2"):
        ok = _untar(file_path, extract_dir)
    elif ext == ".7z":
        ok = _run_extractor(["7z", "x", str(file_path), f"-o{extract_dir}", "-y"], extract_dir)
    elif ext == ".rar":
        ok = _run_extractor(["unrar", "x", "-y", str(file_path), str(extract_dir)], extract_dir)

    if not ok:
        # fallback: 标记为不支持
        fallback = target_dir / f"{stem}_extract_failed.md"
        fallback.write_text(f"# {stem}\n\n压缩包解压失败: {file_path}\n\n格式: {ext}\n", encoding="utf-8")
        return fallback

    # 生成索引文件，列出解压内容
    extracted = sorted(extract_dir.rglob("*"))
    index = target_dir / f"{stem}_index.md"
    lines = [f"# {stem}\n", f"\n来源: {file_path.name}\n", f"解压到: {extract_dir}\n", "\n## 文件清单\n"]
    for f in extracted:
        if f.is_file():
            size = f.stat().st_size
            rel = f.relative_to(extract_dir)
            lines.append(f"- {rel} ({size} bytes)\n")
    index.write_text("".join(lines), encoding="utf-8")
    logger.info(f"解压完成: {file_path.name} → {len(extracted)} 个文件")
    return index


def _unzip(path: Path, dest: Path) -> bool:
    try:
        import zipfile

        with zipfile.ZipFile(path, "r") as z:
            z.extractall(dest)
        return True
    except Exception as e:
        logger.warning(f"zip 解压失败: {e}")
        return False


def _untar(path: Path, dest: Path) -> bool:
    try:
        import os
        import tarfile

        def _safe_filter(members):
            for m in members:
                # 防止路径穿越，但保留相对目录结构
                m.path = os.path.normpath(m.path).lstrip("/")
                if m.path.startswith("..") or os.path.isabs(m.path):
                    logger.warning("跳过危险的 tar 条目: %s", m.path)
                    continue
                yield m

        with tarfile.open(path, "r:*") as tar:
            tar.extractall(dest, members=_safe_filter(tar))
        return True
    except Exception as e:
        logger.warning(f"tar 解压失败: {e}")
        return False


def _run_extractor(cmd: list, dest: Path) -> bool:
    import subprocess

    try:
        subprocess.run(cmd, capture_output=True, timeout=60)
        return dest.exists() and any(dest.iterdir())
    except Exception as e:
        logger.warning(f"外部解压器失败: {e}")
        return False
