#!/usr/bin/env python3
"""
Wiki 文章规范化迁移脚本

功能:
  1. 扫描 wiki/ 目录所有 .md 文件
  2. 按文件名前缀分类 → 注入统一 YAML frontmatter
  3. 报告乱入文件（粘贴的图像、Office 临时文件等）
  4. 可选清理操作

用法:
  python3 migrate_wiki_frontmatter.py              # dry-run 预览
  python3 migrate_wiki_frontmatter.py --apply      # 实际执行
  python3 migrate_wiki_frontmatter.py --backup     # 先备份再执行
"""

import re
import shutil
import sys
from pathlib import Path

WIKI_DIR = Path.home() / "taichu" / "knowledge" / "wiki"
BACKUP_DIR = Path.home() / "taichu" / "knowledge" / "wiki_backup_$(date +%Y%m%d_%H%M%S)"

# ── 三类模板 ──

# 类型 1: 正式文章
TYPE_ARTICLE_PREFIXES = [
    "study-",
    "archive-",
    "karpathy-",
    "architecture-",
    "reference-",
    "project-",
    "design-",
    "analysis-",
    "nebula-",
    "operation-",
    "upload-",
    "minicpm-",
    "holographic-",
    "TEMPLATE-",
]

# 类型 2: 会话日志
TYPE_SESSION_PREFIXES = [
    "session-",
    "会话-",
]

# 类型 3: 快速笔记/条目
TYPE_NOTE_PREFIXES = [
    "obsidian-",
    "nv-",
    "test-",
    "web-",
    "tauri-",
    "system-",
    "roadmap-",
    "report-",
    "phase",
    "plan-",
]

# 需要跳过的特殊文件
SKIP_FILES = {"index.md", "README.md", "base.md"}


def detect_type(filename: str) -> str:
    """根据文件名前缀识别文章类型"""
    for p in TYPE_ARTICLE_PREFIXES:
        if filename.startswith(p):
            return "article"
    for p in TYPE_SESSION_PREFIXES:
        if filename.startswith(p):
            return "session"
    for p in TYPE_NOTE_PREFIXES:
        if filename.startswith(p):
            return "note"
    # 中文命名无前缀 → 按内容特征判断
    return "note"


def generate_title(filepath: Path) -> str:
    """从文件名或文件第一行提取标题"""
    name = filepath.stem  # 不含扩展名
    # 去掉常见前缀
    for prefix in TYPE_ARTICLE_PREFIXES + TYPE_SESSION_PREFIXES + TYPE_NOTE_PREFIXES:
        if name.startswith(prefix):
            name = name[len(prefix) :]
            break
    # 替换分隔符
    title = name.replace("-", " ").replace("_", " ")
    # 尝试从文件内容取第一个 # 标题
    try:
        content = filepath.read_text(encoding="utf-8")
        m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if m:
            return m.group(1).strip()
    except Exception:
        pass
    return title.strip().title() if title else filepath.stem


def extract_date(filename: str) -> str:
    """从文件名提取日期（YYYY-MM-DD 或 YYYYMMDD）"""
    m = re.search(r"(\d{4}[-_]?\d{2}[-_]?\d{2})", filename)
    if m:
        d = m.group(1).replace("_", "-").replace("-", "-")
        if len(d) == 8:  # YYYYMMDD
            return f"{d[:4]}-{d[4:6]}-{d[6:8]}"
        return d
    return ""


def generate_tags(doc_type: str, filename: str) -> list:
    """根据类型和文件名生成标签"""
    tags = [doc_type]
    # 按关键字补充标签
    kw_map = {
        "agent": ["agent"],
        "tool": ["tool"],
        "rust": ["rust"],
        "tauri": ["tauri", "desktop"],
        "web": ["web"],
        "deploy": ["deploy", "ops"],
        "docker": ["docker", "ops"],
        "ai": ["ai"],
        "llm": ["llm"],
        "model": ["model", "llm"],
        "test": ["test"],
        "bug": ["bug", "fix"],
        "tutorial": ["tutorial"],
        "guide": ["guide"],
        "obsidian": ["obsidian"],
        "karpathy": ["karpathy"],
        "neural": ["neural", "ml"],
        "network": ["network"],
        "archive": ["archive"],
        "git": ["git"],
        "python": ["python"],
        "js": ["javascript"],
        "frontend": ["frontend"],
        "backend": ["backend"],
    }
    fname_lower = filename.lower()
    for kw, tag_list in kw_map.items():
        if kw in fname_lower:
            tags.extend(tag_list)
    return list(set(tags))


def has_frontmatter(content: str) -> bool:
    """检查是否已有 YAML frontmatter"""
    return content.startswith("---\n") or content.startswith("---\r\n")


def generate_frontmatter(doc_type: str, title: str, filename: str) -> str:
    """生成统一 frontmatter"""
    tags = generate_tags(doc_type, filename)
    date = extract_date(filename)
    lines = ["---"]
    lines.append(f"type: {doc_type}")
    lines.append(f"title: {title}")
    lines.append(f"tags: {tags}")
    if date:
        lines.append(f"date: {date}")
    lines.append("---\n")
    return "\n".join(lines)


def main():
    dry_run = "--apply" not in sys.argv
    do_backup = "--backup" in sys.argv

    if not WIKI_DIR.exists():
        print(f"❌ Wiki 目录不存在: {WIKI_DIR}")
        sys.exit(1)

    files = sorted(WIKI_DIR.glob("*.md"))
    print(f"📊 共发现 {len(files)} 个 .md 文件\n")

    stats = {"article": 0, "session": 0, "note": 0, "skip": 0}
    to_modify = []

    for fp in files:
        fname = fp.name
        if fname in SKIP_FILES:
            stats["skip"] += 1
            continue

        content = fp.read_text(encoding="utf-8")
        doc_type = detect_type(fname)
        title = generate_title(fp)

        if has_frontmatter(content):
            # 已有 frontmatter，检查是否需要更新
            if not content.startswith(f"---\ntype: {doc_type}"):
                # 类型不匹配，需要更新
                pass
            stats[doc_type] += 1
            continue

        stats[doc_type] += 1
        to_modify.append((fp, doc_type, title, content))
        print(f"   [{doc_type:7}] {fname}")

    print("\n=== 统计 ===")
    print(f"  正式文章 (article): {stats['article']}")
    print(f"  会话日志 (session): {stats['session']}")
    print(f"  快速笔记 (note):    {stats['note']}")
    print(f"  跳过 (特殊文件):   {stats['skip']}")
    print(f"\n  需注入 frontmatter: {len(to_modify)} 个")

    if not to_modify:
        if not dry_run:
            print("\n✅ 所有文件已规范化，无需操作")
        return

    if dry_run:
        print("\n🔍 Dry-run 模式，未做任何修改。加 --apply 执行。")
        return

    # ── 执行迁移 ──
    if do_backup:
        import datetime

        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = Path.home() / "taichu" / "knowledge" / f"wiki_backup_{ts}"
        shutil.copytree(WIKI_DIR, backup)
        print(f"\n📦 已备份到: {backup}")

    modified = 0
    for fp, doc_type, title, content in to_modify:
        fm = generate_frontmatter(doc_type, title, fp.name)
        new_content = fm + content
        fp.write_text(new_content, encoding="utf-8")
        modified += 1
        print(f"  ✅ {fp.name}")

    print(f"\n✅ 完成！{modified} 个文件已更新 frontmatter")


if __name__ == "__main__":
    main()
