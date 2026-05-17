"""调度策略，基于专长匹配和负载惩罚给 agent 打分。"""

# runtime/scheduler/scheduling_policy.py

from typing import Any

# Scheduling weights
LOAD_PENALTY_WEIGHT = 0.5


class SchedulingPolicy:
    """根据任务类型与 agent 专长匹配度加分，负载减分，计算总分。"""

    def score_agent(self, task: Any, agent: Any) -> float:
        """专长匹配加分 + 负载惩罚扣分，返回 agent 对任务的适配分数。"""
        score = 1.0

        # specialization bonus
        if task.task_type == "retrieval" and "retrieval" in agent.agent_id:
            score += 1.0

        # load penalty
        score -= getattr(agent, "load", 0) * LOAD_PENALTY_WEIGHT

        return score
