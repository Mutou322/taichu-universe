"""Agent 基类 — 所有知识宇宙 Agent 的父类

Agent 只能通过 Runtime API 访问知识库，不得直接操作存储层。
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path.home() / "taichu"))

from runtime.memory.api import memory as _memory
from runtime.semantic.runtime import semantic as _semantic


class BaseAgent:
    """知识宇宙 Agent 基类"""

    def __init__(self, agent_id: str, name: str = ""):
        self.agent_id = agent_id
        self.name = name or agent_id
        self.memory = _memory
        self.semantic = _semantic

    def think(self, query: str) -> list[dict]:
        """调用语义搜索获取相关知识"""
        return self.semantic.search(query)

    def recall(self, query: str, top_k: int = 5) -> list[dict]:
        """调用记忆检索"""
        return self.memory.search(query, top_k=top_k)

    def remember(self, doc_id: str, content: str, metadata: dict = None) -> bool:
        """存入一条记忆"""
        return self.memory.store(doc_id, content, metadata)

    def get_name(self) -> str:
        return self.name
