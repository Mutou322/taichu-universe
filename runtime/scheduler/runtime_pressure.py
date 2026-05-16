# runtime/scheduler/runtime_pressure.py


class RuntimePressure:

    def __init__(self):
        self.queue_pressure = 0.0
        self.agent_pressure = {}
        self.memory_pressure = 0.0

    def update_queue_pressure(self, queue_size):
        self.queue_pressure = min(queue_size / 100.0, 1.0)

    def update_agent_pressure(self, agent_id, load):
        self.agent_pressure[agent_id] = load

    def total_pressure(self):
        if not self.agent_pressure:
            return self.queue_pressure

        avg_agent = sum(self.agent_pressure.values()) / len(self.agent_pressure)
        return self.queue_pressure * 0.5 + avg_agent * 0.5
