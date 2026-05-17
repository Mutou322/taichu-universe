"""Phase 9 Nebula UI WebSocket 推送服务，向 demo_full.html 推送节点仿真数据"""

import asyncio
import json
import random
from typing import Any

import websockets

PORT = 8767
NODE_COUNT = 100  # 前端 5000 节点，这里只推 100 个节点的实时数据

nodes = [f"Node_{i}" for i in range(NODE_COUNT)]


async def push_data(websocket: Any) -> None:
    tick = 0
    while True:
        payload: dict[str, Any] = {}
        payload["agent_affinity"] = {node: round(random.uniform(0, 4.99), 2) for node in nodes}

        # evolution — mini-chart
        payload["evolution"] = {
            "generation": tick,
            "fitness_results": [round(random.uniform(0.5, 1.0), 3) for _ in range(6)],
        }

        # archive_hotspots — 每条带 dependencies
        payload["archive_hotspots"] = []
        for i in range(NODE_COUNT):
            dep_count = random.randint(0, 3)
            deps = random.sample(range(NODE_COUNT), min(dep_count, NODE_COUNT))
            payload["archive_hotspots"].append({"file_name": f"Node_{i}_file.pdf", "dependencies": deps})

        await websocket.send(json.dumps(payload))
        tick += 1
        await asyncio.sleep(1.0)


async def handler(websocket: Any) -> None:
    await push_data(websocket)


async def main() -> None:
    async with websockets.serve(handler, "localhost", PORT):
        print(f"Nebula WS server running on ws://localhost:{PORT}")
        print("Open phase9_nebula_demo_full.html in browser.")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
