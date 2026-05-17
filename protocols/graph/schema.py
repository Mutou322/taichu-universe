"""知识图谱数据结构 — 节点与边模型"""

from pydantic import BaseModel


class GraphNode(BaseModel):
    """知识图谱中的概念节点"""

    id: str
    label: str
    category: str = "concept"


class GraphEdge(BaseModel):
    """知识图谱中两个节点之间的一条关系边"""

    source: str
    target: str
    relation_type: str = "references"
