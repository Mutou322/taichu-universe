# runtime/scheduler/load_balancer.py


class LoadBalancer:

    def select_agent(self, agents):
        if not agents:
            return None

        agents = sorted(agents, key=lambda a: getattr(a, "load", 0))
        return agents[0]
