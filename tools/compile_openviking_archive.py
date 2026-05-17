#!/usr/bin/env python3
"""
将 OpenViking 存档数据编译为 wiki 文档格式并写入 wiki/ 目录
"""
import os
import shutil
from pathlib import Path

_TAICHU_HOME = Path(os.environ.get("TAICHU_HOME", str(Path.home() / "taichu"))).expanduser().resolve()
ARCHIVES = _TAICHU_HOME / "archives"
WIKI = _TAICHU_HOME / "knowledge" / "wiki"
OV_SESSIONS = ARCHIVES / "openviking-sessions"
OV_RESOURCES = ARCHIVES / "openviking-resources"
DEST_DIR = WIKI / "_archived"


def compile_sessions() -> None:
    """将会话摘要编译为 wiki 文档"""
    dest = DEST_DIR / "sessions"
    dest.mkdir(parents=True, exist_ok=True)

    # 1. 生成综合会话索引
    overviews = sorted(OV_SESSIONS.glob("*-overview.md"))
    if not overviews:
        print("  跳过 - 无 overview 文件")
        return

    sessions = []
    for f in overviews:
        session_id = f.stem.replace("-overview", "")
        content = f.read_text(encoding="utf-8")
        # 写入独立文档
        (dest / f"{session_id}.md").write_text(
            f"# OpenViking 会话: {session_id}\n\n{content}\n---\nsource:: openviking_workspace/sessions/{session_id}\n",
            encoding="utf-8",
        )
        # 提取第一行作为摘要
        first_line = content.strip().split("\n")[0] if content.strip() else "无摘要"
        sessions.append((session_id, first_line[:80]))

    # 2. 生成会话索引
    lines = ["# OpenViking 会话归档\n", "> 来自 openviking_workspace 的历史会话记录\n", ""]
    for sid, summary in sorted(sessions):
        lines.append(f"- [[_archived/sessions/{sid}]] — {summary}")
    (dest / "index.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"  会话: {len(sessions)} 个编译完成")


def compile_resources() -> None:
    """将学习资源编译为 wiki 文档"""
    dest = DEST_DIR / "resources"
    dest.mkdir(parents=True, exist_ok=True)

    resource_dirs = sorted(OV_RESOURCES.iterdir())
    compiled = 0
    resource_index = ["# OpenViking 学习资源归档\n", "> 来自 openviking_workspace 的学习与探索笔记\n", ""]

    for res_dir in resource_dirs:
        if not res_dir.is_dir():
            continue
        name = res_dir.name
        res_dest = dest / name
        res_dest.mkdir(parents=True, exist_ok=True)

        md_files = sorted(res_dir.glob("**/*.md"))
        if not md_files:
            continue

        for f in md_files:
            if f.is_dir():
                continue
            # 生成相对路径名（不含扩展名）
            rel = f.relative_to(res_dir)
            stem = str(rel.with_suffix("")).replace("/", "-")
            content = f.read_text(encoding="utf-8", errors="replace")
            (res_dest / f"{stem}.md").write_text(
                f"# {name}: {stem}\n\n{content}\n---\nsource:: openviking_workspace/resources/{name}/{rel}\n",
                encoding="utf-8",
            )
            compiled += 1

        # 资源子索引
        sub_index = [f"# {name}\n", f"来源: openviking_workspace/resources/{name}/\n", f"文件数: {len(md_files)}\n", ""]
        for f in md_files:
            rel = f.relative_to(res_dir)
            stem = str(rel.with_suffix("")).replace("/", "-")
            sub_index.append(f"- [[_archived/resources/{name}/{stem}]]")
        (res_dest / "index.md").write_text("\n".join(sub_index), encoding="utf-8")

        resource_index.append(f"- [[_archived/resources/{name}/index]] — {name} ({len(md_files)} 篇)")

    (dest / "index.md").write_text("\n".join(resource_index), encoding="utf-8")
    print(f"  资源: {compiled} 个文档编译完成")


def cleanup_archives_dir() -> None:
    """迁移完成后清理 archives/ 临时目录"""
    if ARCHIVES.exists():
        shutil.rmtree(ARCHIVES)
        print("  archives/ 临时目录已清理")


def main() -> None:
    print("编译 OpenViking 数据到 wiki/...")
    print()
    compile_sessions()
    compile_resources()
    print()
    # 清理临时目录
    cleanup_archives_dir()
    print("完成。")


if __name__ == "__main__":
    main()
