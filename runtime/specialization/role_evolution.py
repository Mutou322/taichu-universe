# runtime/specialization/role_evolution.py


class RoleEvolutionEngine:

    def evolve(self, agent):

        profile = agent.profile

        if profile.expertise_score > 5 and profile.evolution_stage == 1:

            profile.evolution_stage = 2

            print(
                f"[Evolution]",
                agent.agent_id,
                "-> Specialist",
            )

        if profile.expertise_score > 10 and profile.evolution_stage == 2:

            profile.evolution_stage = 3

            print(
                f"[Evolution]",
                agent.agent_id,
                "-> Expert",
            )
