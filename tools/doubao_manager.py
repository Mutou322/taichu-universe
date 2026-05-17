"""doubao_manager — 知识库文件扫描与编译入口（豆包 LLM 驱动）

负责:
  1. 扫描 inbox/ 目录发现新文件
  2. 通过 ingest/pipelines 调度到对应管道（格式转换/OCR/解压）
  3. 调用 kb_models.py compile 使用豆包 LLM 编译为 wiki 词条
  4. 编译完成后刷新语义图谱
"""

import logging
import os
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

_TAICHU_HOME = Path(os.environ.get("TAICHU_HOME", str(Path.home() / "taichu"))).expanduser().resolve()
# 加 ~/taichu 到路径以导入 runtime 模块
sys.path.insert(0, str(_TAICHU_HOME))

_ctx = None


def _get_ctx():
    global _ctx
    if _ctx is None:
        from runtime.bootstrap import init_runtime

        _ctx = init_runtime()
    return _ctx


def _get_paths():
    return _get_ctx()["paths"]


def _get_kb_models():
    return str(_get_paths().kb_models)


def _get_store_dir():
    return _get_paths().get("storage", "raw")


def scan_inbox() -> list[dict]:
    """扫描 inbox 目录，返回待处理文件列表"""
    inbox = Path(_get_paths().ingest.inbox)
    if not inbox.exists():
        return []

    files = []
    for f in sorted(inbox.iterdir()):
        if f.is_file() and not f.name.startswith("."):
            files.append(
                {
                    "path": str(f),
                    "name": f.name,
                    "size": f.stat().st_size,
                    "suffix": f.suffix.lower(),
                }
            )
    return files


def compile_all() -> int:
    """主入口：扫描 inbox → 管道分流 → 豆包 LLM 编译 → wiki"""
    from ingest.pipelines import SUPPORTED, dispatch

    p = _get_paths()
    inbox = Path(p.ingest.inbox)
    wiki_dir = p.wiki_dir
    processed_dir = Path(p.ingest.processed)
    failed_dir = Path(p.ingest.failed)
    store_dir = Path(_get_store_dir())

    inbox.mkdir(parents=True, exist_ok=True)
    wiki_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    failed_dir.mkdir(parents=True, exist_ok=True)
    store_dir.mkdir(parents=True, exist_ok=True)

    files = [f for f in sorted(inbox.iterdir()) if f.is_file() and not f.name.startswith(".")]
    if not files:
        logger.info("inbox 中没有待处理文件")
        return 0

    logger.info(f"发现 {len(files)} 个待处理文件，调度管道编译...")
    converted = 0

    for f in files:
        ext = f.suffix.lower()
        if ext not in SUPPORTED:
            logger.warning(f"不支持的文件格式: {f.name}")
            _move_to(failed_dir, f)
            continue

        logger.info(f"  📄 {f.name}...")

        # 1. 管道调度（格式转换/OCR/解压）
        result = dispatch(f, target_dir=wiki_dir, store_dir=store_dir)

        if not result["ok"]:
            logger.warning(f"  ❌ {f.name}: {result.get('error', '管道处理失败')}")
            _move_to(failed_dir, f)
            continue

        converted_path = Path(result["result"])

        # 2. .md 文件直接发布到 wiki（已在 dispatch 中复制）
        if ext == ".md":
            converted += 1
            _move_to(processed_dir, f)
            logger.info(f"  ✅ {f.name} → wiki (直接发布)")
            continue

        # 3. 其他格式（PDF/Office/图片等）：用豆包 LLM 编译为 wiki 词条
        if _needs_llm_compile(ext):
            kb_result = _compile_with_doubao(converted_path)
            if kb_result["ok"]:
                converted += 1
                _move_to(processed_dir, f)
                logger.info(f"  ✅ {f.name} → 豆包编译完成")
            else:
                logger.warning(f"  ❌ {f.name} 编译失败: {kb_result.get('error', '未知错误')}")
                _move_to(failed_dir, f)
        else:
            # 源码 / 文本类直接发布
            converted += 1
            _move_to(processed_dir, f)
            logger.info(f"  ✅ {f.name} → wiki (源码/文本)")

    logger.info(f"编译完成: {converted}/{len(files)}")
    return converted


def _needs_llm_compile(ext: str) -> bool:
    """需要豆包 LLM 编译的文件类型"""
    return ext in (
        ".pdf",
        ".doc",
        ".docx",
        ".ppt",
        ".pptx",
        ".xls",
        ".xlsx",
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".gif",
        ".bmp",
        ".svg",
        ".html",
        ".htm",
        ".epub",
        ".rtf",
    )


def _compile_with_doubao(file_path: Path) -> dict:
    """调用 kb_models.py compile 使用豆包 LLM 编译"""
    kb_models = _get_kb_models()
    if not Path(kb_models).exists():
        return {"ok": False, "error": f"kb_models.py 不存在: {kb_models}"}
    if not file_path.exists():
        return {"ok": False, "error": f"文件不存在: {file_path}"}

    try:
        result = subprocess.run(
            [sys.executable, kb_models, "compile", str(file_path)],
            capture_output=True,
            text=True,
            timeout=180,
        )
        if result.returncode == 0:
            return {"ok": True, "output": result.stdout.strip()}
        else:
            return {"ok": False, "error": result.stderr.strip() or result.stdout.strip()}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "编译超时(180s)"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _move_to(target_dir: Path, file_path: Path):
    """移动文件到目标目录"""
    dest = target_dir / file_path.name
    # 同名文件加时间戳
    if dest.exists():
        import time

        dest = target_dir / f"{file_path.stem}_{int(time.time())}{file_path.suffix}"
    file_path.rename(dest)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    count = compile_all()
    print(f"CONVERTED: {count}")
    return count


if __name__ == "__main__":
    main()
