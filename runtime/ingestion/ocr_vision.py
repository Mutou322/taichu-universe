"""OCR 视觉提取 — 从原始数据中提取文本（占位，尚未实现实际 OCR）"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class OCRVision:
    """OCR 文本提取器（当前为占位实现）"""

    async def extract(self, raw_data: Any) -> str:
        """从原始数据提取文本（暂返回空字符串）"""
        logger.warning(
            "OCRVision.extract() is a placeholder not yet implemented; " "returning empty string for input of size %d",
            len(raw_data) if raw_data else 0,
        )
        return ""
