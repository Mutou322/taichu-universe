"""
Phase 2 压力测试 — Stress Test Suite

覆盖：
1. 单 Agent latency — 串行执行 N 次 pipeline
2. 多 Agent 并发 — 并行执行 pipeline
3. Graph Expand 内存增长 — 追踪扩展节点数和内存
4. Context Builder token 爆炸 — 验证 token 预算
5. WebSocket 广播压力 — 推送大量 metrics
"""

import asyncio
import time
from pathlib import Path

from config.bootstrap import *


async def test_single_agent(n_runs: int = 10, query: str = "transformer attention"):
    """1. 单 Agent latency — 串行执行 N 次"""
    from runtime.retrieval import run_retrieval_pipeline

    latencies = []
    errors = 0

    for i in range(n_runs):
        start = time.perf_counter()
        try:
            ctx, docs = await run_retrieval_pipeline(query)
            duration = (time.perf_counter() - start) * 1000
            latencies.append(duration)
        except Exception as e:
            errors += 1
            print(f"  ❌ 第 {i+1} 次: {e}")

    if latencies:
        avg = sum(latencies) / len(latencies)
        p95 = sorted(latencies)[int(len(latencies) * 0.95)]
        return {
            "test": "单 Agent latency",
            "runs": n_runs,
            "errors": errors,
            "avg_ms": round(avg, 2),
            "min_ms": round(min(latencies), 2),
            "max_ms": round(max(latencies), 2),
            "p95_ms": round(p95, 2),
        }
    return {"test": "单 Agent latency", "error": "全部失败"}


async def test_multi_agent(n_agents: int = 3, queries: list = None):
    """2. 多 Agent 并发 — 并行执行 pipeline"""
    from runtime.retrieval import run_retrieval_pipeline

    if queries is None:
        queries = [
            "transformer attention",
            "知识库架构",
            "Agent 技能开发",
        ]

    start = time.perf_counter()
    tasks = []
    for i in range(n_agents):
        q = queries[i % len(queries)]
        tasks.append(run_retrieval_pipeline(q))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    duration = (time.perf_counter() - start) * 1000

    errors = sum(1 for r in results if isinstance(r, Exception))
    total_docs = 0
    for r in results:
        if not isinstance(r, Exception):
            total_docs += len(r[1])

    return {
        "test": "多 Agent 并发",
        "agents": n_agents,
        "total_ms": round(duration, 2),
        "errors": errors,
        "total_docs": total_docs,
    }


def test_graph_memory():
    """3. Graph Expand 内存增长"""
    import tracemalloc

    from runtime.retrieval.graph_expand import expand_graph

    tracemalloc.start()
    before = tracemalloc.get_traced_memory()

    # 构造虚拟数据模拟多次扩展
    for _ in range(10):
        expand_graph([{"id": "test", "title": "test"}])

    after = tracemalloc.get_traced_memory()
    growth_kb = (after[0] - before[0]) / 1024

    return {
        "test": "Graph Expand 内存",
        "before_kb": round(before[0] / 1024, 2),
        "after_kb": round(after[0] / 1024, 2),
        "growth_kb": round(growth_kb, 2),
    }


def test_context_token_budget():
    """4. Context Builder token 爆炸验证"""
    from runtime.retrieval.context_builder import build_context

    # 构造大量数据
    docs = [{"text": "A" * 1000}] * 100  # 100 个文档每个 1000 字符
    context = build_context(docs, max_tokens=2000)
    char_count = len(context)
    estimated_tokens = char_count // 4

    return {
        "test": "Context Token 预算",
        "input_docs": len(docs),
        "output_chars": char_count,
        "estimated_tokens": estimated_tokens,
        "budget_respected": estimated_tokens <= 2200,
    }


async def run_all():
    """运行所有压力测试"""
    print("=" * 50)
    print("Phase 2 Stress Test Suite")
    print("=" * 50)

    # 1. 单 Agent
    print("\n[1/4] 单 Agent latency...")
    r1 = await test_single_agent(n_runs=3)
    print(f"  avg={r1.get('avg_ms','?')}ms p95={r1.get('p95_ms','?')}ms errors={r1.get('errors',0)}")

    # 2. 多 Agent
    print("\n[2/4] 多 Agent 并发...")
    r2 = await test_multi_agent(n_agents=3)
    print(f"  {r2['agents']} agents, {r2['total_ms']}ms, errors={r2['errors']}")

    # 3. 内存
    print("\n[3/4] Graph 内存增长...")
    r3 = test_graph_memory()
    print(f"  growth={r3['growth_kb']}KB")

    # 4. Token 预算
    print("\n[4/4] Context Token 预算...")
    r4 = test_context_token_budget()
    print(f"  tokens={r4['estimated_tokens']}, budget_respected={r4['budget_respected']}")

    print("\n" + "=" * 50)
    print("Stress Test Complete")
    print("=" * 50)

    return {"single_agent": r1, "multi_agent": r2, "graph_memory": r3, "context_token": r4}


if __name__ == "__main__":
    asyncio.run(run_all())
