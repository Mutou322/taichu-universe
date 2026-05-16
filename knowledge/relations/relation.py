from dataclasses import dataclass
from enum import Enum


class RelationType(str, Enum):
    """关系类型枚举 — 所有边都应带有类型"""

    RELATED_TO = "related_to"  # 一般关联
    DEPENDS_ON = "depends_on"  # 依赖
    CAUSES = "causes"  # 因果
    EXTENDS = "extends"  # 扩展
    SIMILAR_TO = "similar_to"  # 相似
    CONTRADICTS = "contradicts"  # 矛盾
    PART_OF = "part_of"  # 部分
    REFERENCES = "references"  # 引用（默认）


@dataclass
class SemanticRelation:
    """语义关系 — 节点之间的连接"""

    # 起点
    source: str

    # 终点
    target: str

    # 关系类型
    relation_type: str = RelationType.REFERENCES.value

    # 权重
    weight: float = 1.0
