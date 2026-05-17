#!/usr/bin/env python3
"""太初路径查询 CLI — 供 Rust/Shell 等非 Python 环境调用

用法:
  python3 config/path_cli.py get ingest.raw
  python3 config/path_cli.py get knowledge.wiki
  python3 config/path_cli.py get storage.chroma
"""

import sys

from config.paths import paths


def main() -> None:
    if len(sys.argv) < 3 or sys.argv[1] != "get":
        print("用法: path_cli.py get <key.key.key>", file=sys.stderr)
        sys.exit(1)

    keys = sys.argv[2].split(".")

    try:
        result = paths.get(*keys)
    except (KeyError, TypeError):
        print(f"路径未找到: {sys.argv[2]}", file=sys.stderr)
        sys.exit(1)

    print(result)


if __name__ == "__main__":
    main()
