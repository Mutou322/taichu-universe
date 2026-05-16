"""
Benchmark Dataset — 检索质量基线
用于验证 Retrieval Pipeline 的稳定性和准确性
Phase 1 -> Phase 2 退出的判断依据

每条 query 包含：
- query: 检索语句
- expected_titles: 预期返回的重要词条（模糊匹配）
- category: 查询类别
- min_results: 最少返回条数
"""

BENCHMARK_QUERIES = [
    # ── 架构类 ──
    {
        "query": "知识库架构设计",
        "expected_titles": ["README", "architecture-kb-system"],
        "category": "architecture",
        "min_results": 2,
    },
    {
        "query": "五层架构",
        "expected_titles": ["README"],
        "category": "architecture",
        "min_results": 1,
    },
    {
        "query": "系统边界设计",
        "expected_titles": ["architecture-kb-system"],
        "category": "architecture",
        "min_results": 1,
    },
    # ── AI / LLM ──
    {
        "query": "transformer attention机制",
        "expected_titles": [],
        "category": "ai",
        "min_results": 1,
    },
    {
        "query": "大语言模型推理优化",
        "expected_titles": [],
        "category": "ai",
        "min_results": 1,
    },
    # ── 开发工具 ──
    {
        "query": "Git 常用命令",
        "expected_titles": [],
        "category": "devtools",
        "min_results": 1,
    },
    {
        "query": "Docker 容器部署",
        "expected_titles": [],
        "category": "devtools",
        "min_results": 1,
    },
    # ── Agent ──
    {
        "query": "Agent 技能包开发",
        "expected_titles": [],
        "category": "agent",
        "min_results": 1,
    },
    {
        "query": "多Agent协作框架",
        "expected_titles": [],
        "category": "agent",
        "min_results": 1,
    },
    # ── 知识管理 ──
    {
        "query": "知识图谱构建",
        "expected_titles": [],
        "category": "knowledge",
        "min_results": 1,
    },
    {
        "query": "语义搜索优化",
        "expected_titles": [],
        "category": "knowledge",
        "min_results": 1,
    },
]


def run_benchmark(retrieval_func, top_k: int = 10) -> dict:
    """
    运行 benchmark 测试。

    retrieval_func: callable(query, top_k) -> list[dict]
        每个 dict 至少包含 title 字段

    返回:
    {
        "total": N,
        "passed": N,
        "failed": N,
        "avg_latency_ms": N,
        "results": [{"query": ..., "passed": bool, "hit_count": N, "latency_ms": N}, ...]
    }
    """
    import time

    results = []
    for item in BENCHMARK_QUERIES:
        start = time.perf_counter()
        try:
            hits = retrieval_func(item["query"], top_k)
        except Exception as e:
            results.append(
                {
                    "query": item["query"],
                    "passed": False,
                    "hit_count": 0,
                    "latency_ms": 0,
                    "error": str(e),
                }
            )
            continue
        duration = (time.perf_counter() - start) * 1000

        # 统计命中
        hit_count = len(hits)
        expected = item["expected_titles"]
        expected_hit = 0
        if expected:
            for h in hits:
                title = (h.get("title") or "").lower()
                if any(e.lower() in title for e in expected):
                    expected_hit += 1

        passed = hit_count >= item["min_results"] and expected_hit >= len(expected)

        results.append(
            {
                "query": item["query"],
                "passed": passed,
                "hit_count": hit_count,
                "expected_hit": expected_hit,
                "expected_total": len(expected),
                "min_required": item["min_results"],
                "latency_ms": round(duration, 2),
            }
        )

    passed_count = sum(1 for r in results if r["passed"])
    avg_latency = sum(r["latency_ms"] for r in results) / len(results) if results else 0

    return {
        "total": len(results),
        "passed": passed_count,
        "failed": len(results) - passed_count,
        "pass_rate": round(passed_count / len(results) * 100, 1) if results else 0,
        "avg_latency_ms": round(avg_latency, 2),
        "results": results,
    }
