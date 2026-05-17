"""语义路由 — 根据任务概念匹配最合适的 Agent"""

from typing import Any


class SemanticRouter:
    """按概念重叠度将任务路由到得分最高的 Agent"""

    def route(self, task: Any, agents: list[Any]) -> Any | None:
        """计算每个 Agent 与任务概念的关键词匹配分，返回最高分 Agent"""
        concepts = (task.payload or {}).get("concepts", [])
        scored = []

        for agent in agents:
            score = 0
            for c in concepts:
                if c.lower() in (agent.agent_id or "").lower():
                    score += 1
            scored.append((score, agent))

        scored.sort(key=lambda x: x[0], reverse=True)
        if not scored:
            return None
        return scored[0][1]
