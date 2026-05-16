"""
Phase 2 检索质量 Benchmark — recall / precision / graph coherence

每条 query 包含：
- query: 检索语句
- expected_nodes: 预期返回的关键概念节点
- expected_titles: 预期返回的词条（模糊匹配）
- category: 查询类别
- min_results: 最少返回条数
"""

from pathlib import Path

from config.bootstrap import *

BENCHMARK_QUERIES = [
    # ── 架构类 ──
    {
        "query": "知识库架构设计",
        "expected_nodes": ["架构", "分层", "Runtime"],
        "expected_titles": ["README", "architecture-kb-system"],
        "category": "architecture",
        "min_results": 2,
    },
    {
        "query": "五层架构",
        "expected_nodes": ["ingest", "knowledge", "storage", "runtime", "protocols"],
        "expected_titles": ["README"],
        "category": "architecture",
        "min_results": 1,
    },
    {
        "query": "系统边界设计",
        "expected_nodes": ["跨层", "边界", "约束"],
        "expected_titles": ["architecture-kb-system"],
        "category": "architecture",
        "min_results": 1,
    },
    # ── AI / LLM ──
    {
        "query": "transformer attention机制",
        "expected_nodes": ["Transformer", "Attention", "Self-Attention"],
        "expected_titles": [],
        "category": "ai",
        "min_results": 1,
    },
    {
        "query": "大语言模型推理优化",
        "expected_nodes": ["LLM", "推理", "优化"],
        "expected_titles": [],
        "category": "ai",
        "min_results": 1,
    },
    # ── 开发工具 ──
    {
        "query": "Git 常用命令",
        "expected_nodes": ["Git", "版本控制"],
        "expected_titles": [],
        "category": "devtools",
        "min_results": 1,
    },
    {
        "query": "Docker 容器部署",
        "expected_nodes": ["Docker", "容器", "部署"],
        "expected_titles": [],
        "category": "devtools",
        "min_results": 1,
    },
    # ── Agent ──
    {
        "query": "Agent 技能包开发",
        "expected_nodes": ["Agent", "技能", "SKILL.md"],
        "expected_titles": [],
        "category": "agent",
        "min_results": 1,
    },
    {
        "query": "多Agent协作框架",
        "expected_nodes": ["Agent", "协作", "编排"],
        "expected_titles": [],
        "category": "agent",
        "min_results": 1,
    },
    # ── 知识管理 ──
    {
        "query": "知识图谱构建",
        "expected_nodes": ["图谱", "Graph", "节点"],
        "expected_titles": [],
        "category": "knowledge",
        "min_results": 1,
    },
    {
        "query": "语义搜索优化",
        "expected_nodes": ["语义", "搜索", "检索"],
        "expected_titles": [],
        "category": "knowledge",
        "min_results": 1,
    },
]


def _expected_nodes_found(docs: list, expected_nodes: list) -> dict:
    """计算 recall / precision"""
    if not expected_nodes:
        return {"recall": 1.0, "precision": 1.0, "f1": 1.0}

    # 把所有 title 和 text 拼成字符串
    all_text = " ".join((d.get("title") or "") + " " + (d.get("text") or "") for d in docs).lower()

    hit = 0
    for node in expected_nodes:
        if node.lower() in all_text:
            hit += 1

    recall = hit / len(expected_nodes) if expected_nodes else 1.0
    total_returned = len(docs)
    precision = hit / total_returned if total_returned > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "recall": round(recall, 3),
        "precision": round(precision, 3),
        "f1": round(f1, 3),
        "nodes_hit": hit,
        "nodes_total": len(expected_nodes),
    }


def run_quality_benchmark(retrieval_func, top_k: int = 10) -> dict:
    """
    运行检索质量 benchmark。

    返回 recall / precision / f1 / pass_rate / avg_latency
    """
    import asyncio
    import time

    results = []
    total_recall = 0.0
    total_precision = 0.0
    total_f1 = 0.0

    for item in BENCHMARK_QUERIES:
        start = time.perf_counter()
        try:
            if asyncio.iscoroutinefunction(retrieval_func):
                ctx, docs = asyncio.run(retrieval_func(item["query"]))
            else:
                docs = retrieval_func(item["query"], top_k)
        except Exception as e:
            results.append({"query": item["query"], "error": str(e), "passed": False})
            continue
        duration = (time.perf_counter() - start) * 1000

        # Recall / Precision
        nf = _expected_nodes_found(docs, item.get("expected_nodes", []))
        total_recall += nf["recall"]
        total_precision += nf["precision"]
        total_f1 += nf["f1"]

        # 标题匹配
        expected_titles = item.get("expected_titles", [])
        title_hit = 0
        for d in docs:
            title = (d.get("title") or "").lower()
            if any(e.lower() in title for e in expected_titles):
                title_hit += 1

        passed = len(docs) >= item["min_results"] and title_hit >= len(expected_titles)

        results.append(
            {
                "query": item["query"],
                "passed": passed,
                "latency_ms": round(duration, 2),
                "doc_count": len(docs),
                "title_hit": title_hit,
                "title_expected": len(expected_titles),
                **nf,
            }
        )

    n = len(results)
    avg_recall = total_recall / n if n > 0 else 0
    avg_precision = total_precision / n if n > 0 else 0
    avg_f1 = total_f1 / n if n > 0 else 0
    passed_count = sum(1 for r in results if r["passed"])
    avg_latency = sum(r["latency_ms"] for r in results) / n if n > 0 else 0

    return {
        "total": n,
        "passed": passed_count,
        "failed": n - passed_count,
        "pass_rate": round(passed_count / n * 100, 1) if n > 0 else 0,
        "avg_latency_ms": round(avg_latency, 2),
        "avg_recall": round(avg_recall, 3),
        "avg_precision": round(avg_precision, 3),
        "avg_f1": round(avg_f1, 3),
        "results": results,
    }
