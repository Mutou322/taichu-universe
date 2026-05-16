# runtime/attention/cooperative_attention.py


class CooperativeAttention:

    def reinforce(self, field, node_id, agents):

        total = 0.0

        for agent in agents:

            total += field.get_agent_attention(
                agent.agent_id,
                node_id,
            )

        cooperation_bonus = total * 0.2

        field.node_attention[node_id] += cooperation_bonus

        return cooperation_bonus
