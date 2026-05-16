"""
runtime/retrieval/graph_expand.py — 图谱扩展引擎

负责从知识图谱中扩展节点邻居，带三重爆炸控制：
  A. Pruning: 低分邻居修剪
  B. Decay: 长期不访问节点优先级衰减
  C. Traversal Budget: 每次查询的节点/边数量上限
"""

import time
from collections import deque

from runtime.metrics.timers import metric_timer

# 节点访问记录（用于 decay）
_node_access: dict[str, float] = {}  # {node_id: last_access_timestamp}


def _get_semantic():
    """获取 SemanticRuntime 单例"""
    from runtime.bootstrap import get_semantic

    return get_semantic()


def _neighbors_with_weight(node_id: str) -> list[tuple]:
    """从邻接索引取邻居，返回 [(neighbor_id, edge_weight), ...]（O(1) 查权重）"""
    sem = _get_semantic()
    sem._ensure_graph()
    neighbors = sem.adjacency.get(node_id, set())
    if not neighbors:
        return []

    wmap = sem.weight_map
    return [(nid, wmap.get((node_id, nid), 1.0)) for nid in neighbors]


def _prune_low_score(neighbors: list[tuple], threshold: float = 0.3) -> list[str]:
    """A. 低分邻居修剪：只保留权重 >= threshold 的邻居"""
    return [nid for nid, w in neighbors if w >= threshold]


def _apply_decay(node_id: str, factor: float = 0.95, interval: float = 3600):
    """B. 衰减：长期不访问的节点降低优先级"""
    now = time.time()
    last = _node_access.get(node_id, 0)
    if last > 0 and (now - last) > interval:
        # 超过 interval 秒未访问，衰减 factor
        return factor
    return 1.0


def _neighbors_with_decay(node_id: str, decay_threshold: float = 0.5) -> list[str]:
    """获取邻居并应用 low 分修剪 和 访问衰减"""
    raw = _neighbors_with_weight(node_id)
    # Pruning: 低权重修剪
    pruned = _prune_low_score(raw, threshold=0.3)
    # Decay: 长期不访问的节点可能被过滤
    result = []
    for nid in pruned:
        decay = _apply_decay(nid)
        if decay >= decay_threshold:
            result.append(nid)
    return result


def expand_graph(
    docs: list,
    max_depth: int = 2,
    max_neighbors: int = 5,
    max_nodes_per_query: int = 50,
    max_edges_per_query: int = 200,
) -> list:
    """
    图谱扩展，带完整的爆炸控制。

    C. Traversal Budget 限制：
        - max_nodes_per_query: 每次查询最多扩展的节点数
        - max_edges_per_query: 每次查询最多处理的边数
    """
    with metric_timer("graph_expand"):
        expanded = []
        total_nodes = 0
        total_edges = 0

        for doc in docs:
            node_id = doc.get("id") or doc.get("title", "")
            frontier = deque([(str(node_id), 0)])
            visited = set()
            neighbors_list = []
            doc_edges = 0

            while frontier and total_nodes < max_nodes_per_query and total_edges < max_edges_per_query:
                current_id, depth = frontier.popleft()
                if depth > max_depth or current_id in visited:
                    continue
                visited.add(current_id)
                total_nodes += 1

                # 获取邻居（已应用 pruning + decay）
                neighbors = _neighbors_with_decay(current_id)[:max_neighbors]
                neighbors_list.extend(neighbors)
                doc_edges += len(neighbors)
                total_edges += len(neighbors)

                for n in neighbors:
                    if total_nodes >= max_nodes_per_query or total_edges >= max_edges_per_query:
                        break
                    frontier.append((n, depth + 1))

                # 记录访问时间
                _node_access[current_id] = time.time()

            doc["graph_neighbors"] = neighbors_list
            doc["graph_nodes_expanded"] = len(visited)
            doc["graph_edges_processed"] = doc_edges
            doc["graph_budget_exhausted"] = total_nodes >= max_nodes_per_query or total_edges >= max_edges_per_query
            expanded.append(doc)

    return expanded
