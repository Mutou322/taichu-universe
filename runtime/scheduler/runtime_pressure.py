"""运行时压力监控，综合队列压力和 agent 压力。"""

# runtime/scheduler/runtime_pressure.py

# Pressure blending weights
QUEUE_PRESSURE_WEIGHT = 0.5
AGENT_PRESSURE_WEIGHT = 0.5


class RuntimePressure:
    """追踪队列压力和 agent 级压力，输出加权总压力值。"""

    def __init__(self) -> None:
        self.queue_pressure = 0.0
        self.agent_pressure: dict[str, float] = {}
        self.memory_pressure = 0.0

    def update_queue_pressure(self, queue_size: int) -> None:
        self.queue_pressure = min(queue_size / 100.0, 1.0)

    def update_agent_pressure(self, agent_id: str, load: float) -> None:
        self.agent_pressure[agent_id] = load

    def total_pressure(self) -> float:
        """计算队列压力和 agent 平均压力的加权和（各占 0.5 权重）。"""
        if not self.agent_pressure:
            return self.queue_pressure

        avg_agent = sum(self.agent_pressure.values()) / len(self.agent_pressure)
        return self.queue_pressure * QUEUE_PRESSURE_WEIGHT + avg_agent * AGENT_PRESSURE_WEIGHT
