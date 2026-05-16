# runtime/scheduler/adaptive_scheduler.py

import time


class AdaptiveScheduler:

    def __init__(self, agents):

        self.agents = agents

    def get_ready_nodes(self):

        ready = []

        for agent in self.agents:

            if hasattr(agent, "get_ready_tasks"):
                ready.extend(agent.get_ready_tasks())

        ready.sort(key=lambda t: getattr(t, "priority", 0), reverse=True)

        return ready

    def dispatch(self, node):

        if not self.agents:
            return None

        return self.agents[0]
