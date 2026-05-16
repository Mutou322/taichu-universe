# runtime/specialization/affinity_learning.py


class AffinityLearning:

    def reinforce(self, agent, task_type, success_score):

        profile = agent.profile

        profile.semantic_affinity[task_type] = profile.semantic_affinity.get(task_type, 0.0) + success_score
