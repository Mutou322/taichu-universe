"""图谱运行时 API — 适配层，对接 SemanticRuntime

供 Tauri/Agent 等外部调用，统一接口。
"""

from pathlib import Path
from typing import Optional
from dataclasses import asdict

import sys
sys.path.insert(0, str(Path.home() / "taichu" / "runtime" / "semantic"))
from runtime import semantic

# 事件总线
sys.path.insert(0, str(Path.home() / "taichu" / "runtime" / "events"))
from bus import bus


class GraphRuntime:
    """图谱运行时 API（适配 SemanticRuntime）"""

    def search(self, query: str, limit: int = 20) -> list[dict]:
        return semantic.search(query, limit)

    def related(self, node_id: str) -> list[dict]:
        return semantic.related(node_id)

    @property
    def graph_data(self) -> dict:
        """获取完整图谱数据（供前端渲染，SemanticNode → dict）"""
        graph = semantic._ensure_graph()
        return {
            "nodes": [asdict(n) for n in graph["nodes"]],
            "edges": [asdict(e) for e in graph["edges"]],
        }

    @property
    def node_count(self) -> int:
        return semantic.node_count

    @property
    def edge_count(self) -> int:
        return semantic.edge_count

    def refresh(self):
        semantic.refresh()
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            if loop and loop.is_running():
                loop.create_task(bus.emit("graph:updated", {
                    "node_count": self.node_count,
                    "edge_count": self.edge_count,
                }))
        except RuntimeError:
            pass


# 单例
graph = GraphRuntime()
