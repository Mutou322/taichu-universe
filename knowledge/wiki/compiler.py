"""Wiki 编译器 — 将 Markdown 文件编译为 SemanticNode"""

from pathlib import Path

from knowledge.graph.link_parser import LinkParser
from knowledge.graph.node import SemanticNode


class WikiCompiler:
    """将 wiki/ 目录下的 .md 文件编译为语义节点"""

    def compile(self, path: Path) -> SemanticNode:
        """单个 markdown 文件 → SemanticNode"""
        content = path.read_text(encoding="utf-8", errors="replace")
        stem = path.stem

        links = LinkParser.extract_links(content)
        tags = LinkParser.extract_tags(content)

        # 提取摘要：第一行非空非标题的文本
        summary = ""
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                summary = line[:120]
                break

        # 推断 category（基于目录前缀或前缀标签）
        category = self._infer_category(stem, tags)

        return SemanticNode(
            id=stem,
            title=stem,
            content=content,
            links=links,
            tags=tags,
            category=category,
            summary=summary,
        )

    @staticmethod
    def _infer_category(stem: str, tags: list[str]) -> str:
        """根据文件名前缀或标签推断语义类别"""
        # 文件名前缀推断
        prefix_map = {
            "archive-": "archive",
            "study-": "study",
            "session-": "log",
            "reference-": "reference",
            "obsidian-": "note",
        }
        for prefix, cat in prefix_map.items():
            if stem.startswith(prefix):
                return cat

        # 标签推断
        tag_map = {
            "agent": "agent",
            "memory": "memory",
            "solver": "solver",
            "runtime": "runtime",
            "graph": "graph",
            "ui": "ui",
        }
        for tag, cat in tag_map.items():
            if tag in tags:
                return cat

        return "concept"
