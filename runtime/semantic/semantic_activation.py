"""语义激活引擎 — 将 Agent 任务中的概念提取并激活到语义记忆中"""

from typing import Any


class SemanticActivationEngine:
    """解析任务中的概念并触发语义记忆激活"""

    def __init__(self, memory: Any) -> None:
        self.memory = memory

    def process_task(self, agent_id: str, task: Any) -> None:
        """从任务 payload 中提取概念列表并逐一激活"""
        concepts = (task.payload or {}).get("concepts", [])
        for c in concepts:
            self.memory.activate(concept=c, strength=1.0, source=agent_id)
