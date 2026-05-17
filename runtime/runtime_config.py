# runtime/runtime_config.py


class RuntimeConfig:
    """
    正式 Runtime 全局配置（单例模式）。

    GEP 修改的边界：只改 Runtime 策略，不改知识库。
    Phase 5 Week 5 的 adopt_best_genome 会更新这些值。
    """

    vector_top_k: int = 10
    graph_depth: int = 2
    rerank_weight: float = 0.6
    memory_decay: float = 0.95


runtime_config = RuntimeConfig()
