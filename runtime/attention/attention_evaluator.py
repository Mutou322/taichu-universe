# runtime/attention/attention_evaluator.py

from runtime.attention.attention_map import AttentionMap


class AttentionEvaluator:

    def __init__(self, semantic_gravity_func, rl_module=None):

        self.semantic_gravity_func = semantic_gravity_func
        self.rl_module = rl_module

    def evaluate(self, workflow, agents, experience_feedback=None):

        am = AttentionMap()

        for node in workflow.nodes.values():

            for agent in agents:

                match_score = 0

                if hasattr(agent.profile, "semantic_affinity"):
                    match_score += agent.profile.semantic_affinity.get(
                        node.task_type,
                        0,
                    )

                gravity_score = self.semantic_gravity_func(node.node_id)

                weight = match_score + gravity_score

                if experience_feedback and self.rl_module:

                    feedback = experience_feedback.get(
                        node.node_id,
                        {},
                    ).get(agent.agent_id, 0)

                    weight += feedback

                    self.rl_module.update_agent_affinity(
                        agent,
                        node.task_type,
                        feedback,
                    )

                am.set_weight(
                    node.node_id,
                    agent.agent_id,
                    weight,
                )

        return am
