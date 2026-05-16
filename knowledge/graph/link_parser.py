import re


class LinkParser:
    """双链解析器 — 从 Markdown 文本中提取 [[链接]] 和标签"""

    # wiki 双链模式: [[target]] 或 [[target|display]]
    WIKILINK_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")

    # 标签模式: #tag (仅行首或空格前)
    TAG_PATTERN = re.compile(r"(?:^|\s)#([a-zA-Z0-9_\-\u4e00-\u9fff]+)")

    @staticmethod
    def extract_links(text: str) -> list[str]:
        """提取所有 [[双链]]，返回目标名称列表（去掉 display 部分）"""
        links = []
        for match in LinkParser.WIKILINK_PATTERN.finditer(text):
            target = match.group(1)
            # 支持 [[target|display]] 语法
            target = target.split("|")[0].strip()
            if target:
                links.append(target)
        return links

    @staticmethod
    def extract_tags(text: str) -> list[str]:
        """提取 #tag 标签"""
        return [m.group(1) for m in LinkParser.TAG_PATTERN.finditer(text)]
