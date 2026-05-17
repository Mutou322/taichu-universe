"""WebSocket 事件消息结构"""

from typing import Any

from pydantic import BaseModel


class WSMessage(BaseModel):
    """WebSocket 消息信封，包含消息类型和负载数据"""

    type: str
    payload: dict[str, Any]
