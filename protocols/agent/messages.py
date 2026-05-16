from typing import Optional

from pydantic import BaseModel


class AgentQuery(BaseModel):
    agent_id: str
    query: str
    context: Optional[dict] = None


class AgentResponse(BaseModel):
    success: bool
    result: str
    data: Optional[dict] = None
