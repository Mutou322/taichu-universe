"""WebSocket 实时接口 — 事件广播给所有连接的客户端

启动:
    python3 interfaces/websocket/server.py
"""

from pathlib import Path
import sys
import asyncio
import json

sys.path.insert(0, str(Path.home() / "taichu"))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

from runtime.events.bus import bus

app = FastAPI(title="太初 WebSocket 实时接口")

connected_clients: list[WebSocket] = []


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connected_clients.append(ws)
    print(f"[WS] 客户端连接: {len(connected_clients)} 个")

    try:
        while True:
            # 等待客户端消息（心跳保持）
            data = await ws.receive_text()
            if data == "ping":
                await ws.send_text("pong")
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[WS] 错误: {e}")
    finally:
        if ws in connected_clients:
            connected_clients.remove(ws)
        print(f"[WS] 客户端断开: {len(connected_clients)} 个")


# EventBus → WebSocket 桥接
async def _ws_broadcast(event: str, data: dict):
    payload = json.dumps({"event": event, "data": data})
    dead = []
    for ws in connected_clients:
        try:
            await ws.send_text(payload)
        except Exception:
            dead.append(ws)
    for ws in dead:
        if ws in connected_clients:
            connected_clients.remove(ws)


# 订阅所有事件类型
@bus.on("memory:stored")
def on_memory_stored(data):
    try:
        loop = asyncio.get_running_loop()
        if loop and loop.is_running():
            loop.create_task(_ws_broadcast("memory:stored", data))
    except RuntimeError:
        pass


@bus.on("memory:deleted")
def on_memory_deleted(data):
    try:
        loop = asyncio.get_running_loop()
        if loop and loop.is_running():
            loop.create_task(_ws_broadcast("memory:deleted", data))
    except RuntimeError:
        pass


if __name__ == "__main__":
    print("[WS] 启动 WebSocket 服务器 ws://127.0.0.1:8767/ws")
    uvicorn.run(app, host="127.0.0.1", port=8767)
