# runtime/visualization/sample_node_ws_server.py
# Phase 9 Nebula UI — WebSocket 推送服务 (适配 demo_full.html)
# 用法: python3 sample_node_ws_server.py
# 然后浏览器打开 phase9_nebula_demo_full.html

import asyncio
import json
import random

import websockets

PORT = 8767
NODE_COUNT = 100  # 前端 5000 节点，这里只推 100 个节点的实时数据

nodes = [f"Node_{i}" for i in range(NODE_COUNT)]


async def push_data(websocket):
    tick = 0
    while True:
        payload = {}

        # semantic_gravity — 节点引力
        payload["semantic_gravity"] = {node: round(random.uniform(0, 5), 2) for node in nodes}

        # attention_map — 热点权重 (halo glow)
        payload["attention_map"] = {node: round(random.uniform(0, 5), 2) for node in nodes}

        # agent_affinity — 映射 clusterId
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


async def handler(websocket):
    await push_data(websocket)


async def main():
    async with websockets.serve(handler, "localhost", PORT):
        print(f"Nebula WS server running on ws://localhost:{PORT}")
        print("Open phase9_nebula_demo_full.html in browser.")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
