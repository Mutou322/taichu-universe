#!/usr/bin/env python3
"""
Inject created_at into wiki files that lack it.

Strategy:
1. If frontmatter has 'date' → use it as created_at
2. Else → use file mtime (OS modification time)

Also initialize access_count: 0 and last_accessed_at: null
for files that don't have them.
"""
import os
import re
from datetime import datetime
from pathlib import Path

_TAICHU_HOME = Path(os.environ.get("TAICHU_HOME", str(Path.home() / "taichu"))).expanduser().resolve()
WIKI_DIR = _TAICHU_HOME / "knowledge" / "wiki"
SKIP_FILES = {"index.md", "README.md", "base.md"}


def split_frontmatter(text: str) -> tuple[str, str]:
    """Split markdown text into (frontmatter_text, body)."""
    if not text.startswith("---"):
        return "", text

    rest = text[3:]
    if rest.startswith("\n"):
        rest = rest[1:]
    else:
        return "", rest

    if rest.startswith("---"):
        return "", rest[3:].lstrip("\n")

    match = re.search(r"\n---", rest)
    if not match:
        return "", text

    fm_text = rest[: match.start()]
    body = rest[match.end() :]
    if body.startswith("\n"):
        body = body[1:]
    return fm_text, body


def parse_date_from_fm(fm_text: str) -> str | None:
    """Try to extract date from raw frontmatter text."""
    m = re.search(r"^date:\s*(.+)$", fm_text, re.MULTILINE)
    if m:
        return m.group(1).strip().strip("'\"")
    return None


def has_field(fm_text: str, field: str) -> bool:
    return re.search(rf"^{field}:", fm_text, re.MULTILINE) is not None


def inject_fields(fm_text: str, created_at: str, now_str: str) -> tuple[str, list[str]]:
    """Add created_at, access_count, last_accessed_at if missing."""
    lines = fm_text.split("\n") if fm_text.strip() else []
    new_lines = list(lines)
    insert_pos = len(new_lines)  # default: before closing ---

    # Find insertion point: after existing fields
    for i, line in enumerate(lines):
        if line.strip() == "":
            insert_pos = i
            break

    added = []

    if not has_field(fm_text, "created_at"):
        new_lines.insert(insert_pos, f'created_at: "{created_at}"')
        added.append(f"created_at={created_at}")
        insert_pos += 1

    if not has_field(fm_text, "access_count"):
        new_lines.insert(insert_pos, "access_count: 0")
        added.append("access_count=0")
        insert_pos += 1

    if not has_field(fm_text, "last_accessed_at"):
        new_lines.insert(insert_pos, "last_accessed_at: null")
        added.append("last_accessed_at=null")
        insert_pos += 1

    return "\n".join(new_lines), added


def main() -> None:
    total = 0
    updated = 0
    skipped = 0
    errors = 0
    now_str = datetime.now().strftime("%Y-%m-%d")

    for md_file in sorted(WIKI_DIR.rglob("*.md")):
        if md_file.name in SKIP_FILES:
            skipped += 1
            continue

        total += 1
        try:
            text = md_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            print(f"  ⚠ 读取失败 {md_file.name}: {e}")
            errors += 1
            continue

        fm_text, body = split_frontmatter(text)
        if not fm_text.strip():
            skipped += 1
            continue

        # Determine created_at
        created_at = parse_date_from_fm(fm_text)
        if not created_at:
            # Fallback to file mtime
            mtime = os.path.getmtime(md_file)
            created_at = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

        # Inject fields
        new_fm, added = inject_fields(fm_text, created_at, now_str)
        if not added:
            continue  # nothing changed

        # Reconstruct file
        new_text = f"---\n{new_fm}\n---\n{body}"
        md_file.write_text(new_text, encoding="utf-8")
        print(f"  ✓ {md_file.name}: {', '.join(added)}")
        updated += 1

    print(f"\n完成: {total} 文件扫描, {updated} 更新, {skipped} 跳过, {errors} 错误")


if __name__ == "__main__":
    main()
