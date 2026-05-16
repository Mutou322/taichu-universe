# runtime/scheduler/scheduling_policy.py


class SchedulingPolicy:

    def score_agent(self, task, agent):
        score = 1.0

        # specialization bonus
        if task.task_type == "retrieval" and "retrieval" in agent.agent_id:
            score += 1.0

        # load penalty
        score -= getattr(agent, "load", 0) * 0.5

        return score
