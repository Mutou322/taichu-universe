import time
import uuid
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TraceNode:
    id: str
    name: str
    start_time: float
    end_time: Optional[float] = None
    children: List["TraceNode"] = field(default_factory=list)

    def duration_ms(self):
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0


class RuntimeTracer:
    def __init__(self):
        self.root_nodes = []
        self._stack = []  # 当前节点栈

    def start(self, name: str):
        node = TraceNode(id=str(uuid.uuid4()), name=name, start_time=time.time())

        if self._stack:
            # 有父节点 → 挂到父节点的 children
            parent = self._stack[-1]
            parent.children.append(node)
        else:
            # 无父节点 → 作为根
            self.root_nodes.append(node)

        self._stack.append(node)
        return node

    def finish(self, node: TraceNode):
        node.end_time = time.time()
        # 从栈中弹出
        if self._stack and self._stack[-1].id == node.id:
            self._stack.pop()

    def clear(self):
        """清空所有 trace"""
        self.root_nodes.clear()
        self._stack.clear()


runtime_tracer = RuntimeTracer()
