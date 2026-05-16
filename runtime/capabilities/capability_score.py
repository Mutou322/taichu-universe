# runtime/capabilities/capability_score.py


class CapabilityScore:

    def score(self, task, capabilities):

        required = getattr(task, "required_capabilities", [])

        total = 0

        for r in required:

            for c in capabilities:

                if c.name == r:
                    total += c.score

        return total
