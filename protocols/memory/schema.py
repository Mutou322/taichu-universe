from pydantic import BaseModel


class MemoryRecord(BaseModel):
    id: str
    content: str
    metadata: dict = {}
