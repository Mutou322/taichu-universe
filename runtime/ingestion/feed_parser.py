"""Feed 解析器 — 将原始字节或字符串统一解码为文本"""


class FeedParser:
    """原始数据解码器，将 bytes/str 统一转为 UTF-8 字符串"""

    async def parse(self, raw_data: bytes | str) -> str:

        if isinstance(raw_data, bytes):
            return raw_data.decode("utf-8", errors="replace")

        if isinstance(raw_data, str):
            return raw_data

        return str(raw_data)
