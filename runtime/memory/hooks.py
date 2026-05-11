"""记忆事件钩子 — MemoryRuntime → EventBus 桥接

MemoryRuntime 的 store/delete 操作触发后，自动 emit 事件。
其他模块（WebSocket、Graph、Logger）通过订阅事件获得通知。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "taichu"))
from runtime.events.bus import bus


def on_memory_store(doc_id: str, content: str, metadata: dict = None):
    """MemoryRuntime 存储后自动触发"""
    bus.emit_async("memory:stored", {
        "id": doc_id,
        "content_preview": (content or "")[:200],
        "metadata": metadata or {},
    })


def on_memory_delete(doc_id: str):
    """MemoryRuntime 删除后自动触发"""
    bus.emit_async("memory:deleted", {
        "id": doc_id,
    })
