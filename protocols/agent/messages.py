"""Agent 消息协议 — 查询/响应数据结构"""

from typing import Optional

from pydantic import BaseModel


class AgentQuery(BaseModel):
    """Agent 查询请求"""

    agent_id: str
    query: str
    context: Optional[dict] = None


class AgentResponse(BaseModel):
    """Agent 查询响应"""

    success: bool
    result: str
    data: Optional[dict] = None
