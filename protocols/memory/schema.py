"""记忆存储数据结构"""

from pydantic import BaseModel


class MemoryRecord(BaseModel):
    """Agent 记忆记录，包含内容与元数据"""

    id: str
    content: str
    metadata: dict = {}
