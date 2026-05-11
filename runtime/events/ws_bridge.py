"""EventBus → WebSocket 桥接

监听 Runtime 事件并通过 WebSocket 广播给所有连接的客户端。
实际实现见 interfaces/websocket/server.py 中的 _ws_broadcast。
此文件作为桥接定义层。
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path.home() / "taichu"))
from runtime.events.bus import bus


# 定义事件 → WebSocket 的映射关系（供 ws server 注册使用）
EVENT_WS_MAP = {
    "memory:stored": "memory:stored",
    "memory:deleted": "memory:deleted",
    "graph:updated": "graph:updated",
}


def register_ws_handlers(broadcast_fn):
    """注册所有事件处理器到 WebSocket 广播函数"""
    for event in EVENT_WS_MAP:
        bus.on(event, lambda data, ev=event: broadcast_fn(ev, data))
