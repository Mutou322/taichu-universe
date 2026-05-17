"""运行时追踪器，提供树形调用链追踪能力，支持异步上下文传播"""

import contextvars
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

_stack_var: contextvars.ContextVar[list] = contextvars.ContextVar("trace_stack")


@dataclass
class TraceNode:
    """追踪树节点，记录操作名称、起止时间及子节点"""

    id: str
    name: str
    start_time: float
    end_time: Optional[float] = None
    children: list["TraceNode"] = field(default_factory=list)

    def duration_ms(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0


class RuntimeTracer:
    """运行时调用链追踪器，使用 contextvars 维护异步安全的追踪栈"""

    def __init__(self) -> None:
        self.root_nodes: list[TraceNode] = []

    def _get_stack(self) -> list:
        try:
            return _stack_var.get()
        except LookupError:
            s: list = []
            _stack_var.set(s)
            return s

    def start(self, name: str) -> TraceNode:
        node = TraceNode(id=str(uuid.uuid4()), name=name, start_time=time.time())

        stack = self._get_stack()
        if stack:
            # 有父节点 → 挂到父节点的 children
            parent = stack[-1]
            parent.children.append(node)
        else:
            # 无父节点 → 作为根
            self.root_nodes.append(node)

        stack.append(node)
        return node

    def finish(self, node: TraceNode) -> None:
        node.end_time = time.time()
        stack = self._get_stack()
        if stack and stack[-1].id == node.id:
            stack.pop()

    def clear(self) -> None:
        """清空所有 trace"""
        self.root_nodes.clear()


runtime_tracer = RuntimeTracer()
