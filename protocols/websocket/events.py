from pydantic import BaseModel
from typing import Any


class WSMessage(BaseModel):
    type: str
    payload: dict[str, Any]
