from pydantic import BaseModel


class GraphNode(BaseModel):
    id: str
    label: str
    category: str = "concept"


class GraphEdge(BaseModel):
    source: str
    target: str
    relation_type: str = "references"
