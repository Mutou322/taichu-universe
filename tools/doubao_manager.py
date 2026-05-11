#!/usr/bin/env python3
"""
豆包 LLM 知识管家 — 将 inbox/ + raw/ 中的文件转换为 wiki/ 知识文档

使用 core/ingest/router.py 多模态 ingest 流水线：
  text → 直接读取
  pdf/office → markitdown 转换
  image → 豆包 Vision API 理解
"""

import re
import subprocess
import sys
from pathlib import Path

# 统一配置中心
sys.path.insert(0, str(Path.home() / "taichu" / "config"))
from paths import paths

WIKI_DIR = paths.wiki_dir
INBOX_DIR = paths.inbox_dir
VAULT = paths.root
KB_MODELS = Path.home() / ".hermes" / "skills" / "wiki-knowledge-base" / "scripts" / "kb_models.py"

# 将 core/ 加入 sys.path
CORE_DIR = VAULT / "tools" / "core"
if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))


def compile_md(f: Path) -> int:
    """直接编译 .md 文件（不分 inbox/raw）"""
    try:
        result = subprocess.run(
            [sys.executable, str(KB_MODELS), "compile", str(f)],
            capture_output=True, text=True, timeout=180
        )
        output = result.stdout + result.stderr
        if result.returncode == 0 and "Written" in output:
            print("OK")
            return 1
        else:
            print(f"失败: {output.strip()[-150:]}")
            return 0
    except subprocess.TimeoutExpired:
        print("超时(180s)")
        return 0
    except Exception as e:
        print(f"错误: {e}")
        return 0


def process_inbox() -> int:
    if not INBOX_DIR.exists():
        print("inbox/ 目录不存在")
        return 0

    from core.ingest.router import ingest_file

    converted = 0

    # 处理 inbox/ 的所有文件
    for f in sorted(INBOX_DIR.iterdir()):
        if f.is_dir():
            continue
        print(f"  {f.name}...", end=" ")

        if f.suffix == ".md":
            # .md 文件直接编译
            converted += compile_md(f)
            f.unlink()
            continue

        # 通过 ingest router 提取内容
        try:
            ingested = ingest_file(f)
        except ValueError as e:
            print(f"跳过: {e}")
            f.unlink()
            continue

        text = ingested.text
        if not text.strip():
            print("跳过: 内容为空")
            f.unlink()
            continue

        # 对于图片/UI 截图，Vision 返回的内容可能较长，不截断
        stem = re.sub(r'[\\/*?:"<>|]', "_", f.stem)
        target_name = f"{stem}.md"
        tmp_file = INBOX_DIR / target_name

        # 图片类内容不截断，完整保留 Vision 分析结果
        if ingested.modality == "image":
            tmp_file.write_text(
                f"# {stem}\n\n来源: {f.name}\n\n{text}",
                encoding="utf-8"
            )
        else:
            tmp_file.write_text(
                f"# {stem}\n\n来源: {f.name}\n\n{text[:8000]}",
                encoding="utf-8"
            )

        converted += compile_md(tmp_file)

        if tmp_file.exists():
            tmp_file.unlink()
        f.unlink()

    # 处理 raw/ 中的 .md
    raw_dir = VAULT / "raw"
    if raw_dir.exists():
        for f in sorted(raw_dir.iterdir()):
            if f.suffix == ".md" and f.is_file():
                wiki_target = WIKI_DIR / f.name
                if wiki_target.exists():
                    continue  # 已编译过
                print(f"  [{f.name}]...", end=" ")
                converted += compile_md(f)

    return converted


def main():
    count = process_inbox()
    if count > 0:
        print(f"\nCONVERTED:{count}")
        # After successful compilation, trigger ChromaDB incremental index update
        chroma_idx = VAULT / "tools" / "build_chromadb_index.py"
        if chroma_idx.exists():
            try:
                print("  [ChromaDB] 更新向量索引...")
                result = subprocess.run(
                    [sys.executable, str(chroma_idx), "incremental"],
                    capture_output=True, text=True, timeout=120,
                )
                if result.returncode == 0:
                    print(f"  [ChromaDB] 增量索引更新完成")
                else:
                    print(f"  [ChromaDB] 更新失败: {result.stderr.strip()[-120:]}")
            except Exception as e:
                print(f"  [ChromaDB] 更新异常: {e}")
    else:
        print("没有需要转换的文件。")


if __name__ == "__main__":
    main()
