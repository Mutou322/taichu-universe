"""太初知识宇宙 CLI 接口

用法:
    python3 interfaces/cli/main.py search <query>
    python3 interfaces/cli/main.py status
    python3 interfaces/cli/main.py graph-stats
"""

import sys

from runtime.memory.api import memory
from runtime.semantic.runtime import semantic


def cmd_search(query: str, limit: int = 5):
    results = memory.search(query, top_k=limit)
    if not results:
        print("未找到结果")
        return
    print(f"搜索结果 ({len(results)}):")
    for i, r in enumerate(results):
        print(f"  {i+1}. {r['title']} (score: {r['score']:.4f})")
        if r.get("text"):
            preview = r["text"][:100]
            print(f"     {preview}")


def cmd_status():
    print("知识库状态:")
    print(f"  图谱节点: {semantic.node_count}")
    print(f"  图谱边数: {semantic.edge_count}")
    print(f"  记忆条目: {memory.count}")


def cmd_graph_stats():
    graph = semantic._ensure_graph()
    categories = {}
    for n in graph["nodes"]:
        cat = n.category
        categories[cat] = categories.get(cat, 0) + 1

    print(f"节点类别分布 ({sum(categories.values())}):")
    for cat, cnt in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {cnt}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "search" and len(sys.argv) >= 3:
        cmd_search(" ".join(sys.argv[2:]))
    elif cmd == "status":
        cmd_status()
    elif cmd == "graph-stats":
        cmd_graph_stats()
    else:
        print(f"未知命令: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
