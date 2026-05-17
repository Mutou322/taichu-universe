"""适应度评估器，综合延迟、连贯性和记忆命中率。"""

# runtime/evolution/fitness.py

from typing import Any


class FitnessEvaluator:
    """根据 latency/coherence/memory_hit 加权计算适应度分数。"""

    @staticmethod
    def evaluate(metrics: dict[str, Any]) -> float:

        latency = metrics["latency"]
        coherence = metrics["coherence"]
        memory_hit = metrics["memory_hit"]

        fitness = 0.5 * coherence + 0.3 * memory_hit - 0.2 * latency

        return fitness
