#!/usr/bin/env python3
"""quick_ingest — 扔文件 → 得 wiki 的极简 CLI 工具

用法:
    python3 tools/quick_ingest.py mydoc.pdf          # 单个文件
    python3 tools/quick_ingest.py mynote.md           # markdown 直接入库
    python3 tools/quick_ingest.py image.png           # 图片 OCR 编译
    python3 tools/quick_ingest.py *.pdf               # 批量处理
    python3 tools/quick_ingest.py --watch             # 监控 inbox 自动编译
"""

import argparse
import glob as _glob
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

_TAICHU_HOME = Path(os.environ.get("TAICHU_HOME", str(Path.home() / "taichu"))).expanduser().resolve()

# ── 路径初始化 ──────────────────────────────────────────────
sys.path.insert(0, str(_TAICHU_HOME))
from config.paths import paths  # noqa: E402

# 支持的文件扩展名（与 ingest/pipelines/__init__.py 保持同步）
SUPPORTED: set[str] = {
    # markdown — 直接复制到 wiki
    ".md",
    # 文档格式 — 送 inbox → doubao LLM 编译
    ".pdf",
    ".docx",
    ".pptx",
    ".html",
    ".htm",
    ".txt",
    ".csv",
    ".xlsx",
    ".epub",
    # 图片 — OCR → Markdown → 编译
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".bmp",
    # 源码 — 直接发布
    ".py",
    ".js",
    ".ts",
    ".yaml",
    ".toml",
}

DOUBAO_PATH = _TAICHU_HOME / "tools" / "doubao_manager.py"
POLL_INTERVAL = 5  # watch 模式轮询间隔（秒）
COMPILE_TIMEOUT = 300  # 编译超时（秒）


# ── 辅助函数 ────────────────────────────────────────────────


def _expand_globs(patterns: list[str]) -> list[Path]:
    """将 glob 模式展开为实际文件路径列表。"""
    files: list[Path] = []
    for pat in patterns:
        if any(c in pat for c in "*?["):
            matches = _glob.glob(pat)
            if not matches:
                print(f"✗ {pat} → 没有匹配的文件")
            for m in matches:
                files.append(Path(m).resolve())
        else:
            files.append(Path(pat).expanduser().resolve())
    return files


def _run_doubao_manager() -> tuple[bool, str]:
    """调用 doubao_manager.py 编译 inbox 中的全部文件。

    Returns:
        (ok, output_text)
    """
    if not DOUBAO_PATH.exists():
        msg = "doubao_manager.py 未找到，请检查环境"
        print(f"✗ {msg}")
        return False, msg

    try:
        result = subprocess.run(
            [sys.executable, str(DOUBAO_PATH)],
            capture_output=True,
            text=True,
            timeout=COMPILE_TIMEOUT,
            cwd=str(_TAICHU_HOME),
        )
        output = result.stdout.strip()
        if result.returncode == 0:
            return True, output
        else:
            err = result.stderr.strip() or output or "未知错误"
            return False, err
    except subprocess.TimeoutExpired:
        msg = f"编译超时 ({COMPILE_TIMEOUT}s)"
        print(f"✗ {msg}")
        return False, msg
    except Exception as exc:
        msg = f"编译异常: {exc}"
        print(f"✗ {msg}")
        return False, msg


# ── 核心逻辑 ────────────────────────────────────────────────


def process_files(file_paths: list[Path]) -> int:
    """处理文件列表，返回失败计数。"""
    wiki_dir = paths.wiki_dir
    inbox_dir = paths.inbox_dir

    wiki_dir.mkdir(parents=True, exist_ok=True)
    inbox_dir.mkdir(parents=True, exist_ok=True)

    md_files: list[Path] = []
    non_md_files: list[Path] = []
    errors = 0

    for src in file_paths:
        if not src.exists():
            print(f"✗ {src.name} → 文件不存在")
            errors += 1
            continue

        ext = src.suffix.lower()
        if ext not in SUPPORTED:
            print(f"✗ {src.name} → 不支持的文件格式")
            errors += 1
            continue

        if ext == ".md":
            dest = wiki_dir / src.name
            shutil.copy2(src, dest)
            print(f"✓ {src.name} → 已发布到 wiki/")
            md_files.append(src)
        else:
            dest = inbox_dir / src.name
            shutil.copy2(src, dest)
            non_md_files.append(src)

    if non_md_files:
        names = ", ".join(f.name for f in non_md_files)
        print(f"放入 inbox: {names}")
        ok, output = _run_doubao_manager()
        if ok:
            # 显示 doubao_manager 的编译日志
            if output:
                for line in output.splitlines():
                    print(f"  {line}")
            for f in non_md_files:
                print(f"✓ {f.name} → 已编译入库")
        else:
            if output:
                print(f"  {output}")
            for f in non_md_files:
                print(f"✗ {f.name} → 编译失败")
            errors += len(non_md_files)

    return errors


def watch_loop() -> int:
    """监控 inbox 目录，每 POLL_INTERVAL 秒扫描一次新文件并自动编译。"""
    inbox_dir = paths.inbox_dir
    inbox_dir.mkdir(parents=True, exist_ok=True)

    print(f"监控 {inbox_dir}（每 {POLL_INTERVAL} 秒扫描，Ctrl+C 退出）")

    known: set[Path] = set()
    if inbox_dir.exists():
        known = {f for f in inbox_dir.iterdir() if f.is_file() and not f.name.startswith(".")}

    try:
        while True:
            time.sleep(POLL_INTERVAL)
            if not inbox_dir.exists():
                continue

            current = {f for f in inbox_dir.iterdir() if f.is_file() and not f.name.startswith(".")}
            new_files = current - known

            if new_files:
                names = ", ".join(f.name for f in new_files)
                print(f"\n发现新文件: {names}")
                ok, output = _run_doubao_manager()
                if ok:
                    if output:
                        for line in output.splitlines():
                            print(f"  {line}")
                    print("✓ 编译完成")
                else:
                    if output:
                        print(f"  {output}")
                    print("✗ 编译失败")

            known = current

    except KeyboardInterrupt:
        print("\n已退出监控")
        return 0


# ── 入口 ────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        description="扔文件 → 得 wiki — 极简知识库录入工具",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="要录入的文件（可使用通配符，如 *.pdf）",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="监控 inbox 目录，自动编译新文件",
    )
    args = parser.parse_args()

    if args.watch:
        return watch_loop()

    if not args.files:
        parser.print_help()
        return 1

    file_paths = _expand_globs(args.files)
    if not file_paths:
        return 1

    errors = process_files(file_paths)
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
