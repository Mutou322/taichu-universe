# runtime/evolution/fitness.py


class FitnessEvaluator:

    @staticmethod
    def evaluate(metrics):

        latency = metrics["latency"]
        coherence = metrics["coherence"]
        memory_hit = metrics["memory_hit"]

        fitness = 0.5 * coherence + 0.3 * memory_hit - 0.2 * latency

        return fitness
