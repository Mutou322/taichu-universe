from typing import Any

from pydantic import BaseModel


class WSMessage(BaseModel):
    type: str
    payload: dict[str, Any]
