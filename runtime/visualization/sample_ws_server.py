# runtime/visualization/sample_ws_server.py

import asyncio
import json
import random

import websockets

PORT = 8767

# 默认参数
shard_count = 4
agent_count = 4
node_count = 20
cluster_count = 5
sleep_time = 1.0


def generate_nodes():
    return [f"Node_{i}" for i in range(node_count)]


def generate_agents():
    return [f"Agent_{i}" for i in range(agent_count)]


async def send_metrics(websocket):

    tick = 0
    global shard_count, agent_count, node_count, sleep_time

    while True:

        nodes = generate_nodes()
        agents = generate_agents()

        # ---------------- Evolution Metrics ----------------
        evolution = {
            "generation": tick,
            "fitness_results": [random.uniform(0.5, 1.0) for _ in range(6)],
            "best_genome": {
                "vector_top_k": random.randint(5, 10),
                "graph_depth": random.randint(2, 4),
            },
        }

        # ---------------- Attention + Semantic Gravity ----------------
        attention_map = {node: random.random() * 5 for node in nodes}

        semantic_gravity = {node: random.randint(0, 5) for node in nodes}

        # ---------------- GBrain clusters ----------------
        clusters = {i: random.sample(nodes, k=min(random.randint(2, 6), len(nodes))) for i in range(cluster_count)}

        gbrain = {
            "clusters": clusters,
            "gravity": {i: random.randint(0, 20) for i in clusters},
        }

        # ---------------- Hotspot clusters ----------------
        hotspot_clusters = {i: random.sample(nodes, k=min(random.randint(1, 3), len(nodes))) for i in range(3)}

        # ---------------- Shard info ----------------
        node_shards = {node: random.randint(0, shard_count - 1) for node in nodes}

        agent_shards = {agent: random.randint(0, shard_count - 1) for agent in agents}

        shard_info = {
            "node_shards": node_shards,
            "agent_shards": agent_shards,
        }

        # ---------------- Compose payload ----------------
        payload = json.dumps(
            {
                "evolution": evolution,
                "attention_map": attention_map,
                "semantic_gravity": semantic_gravity,
                "gbrain": gbrain,
                "hotspot_clusters": hotspot_clusters,
                "shard_info": shard_info,
            }
        )

        await websocket.send(payload)

        tick += 1

        await asyncio.sleep(sleep_time)


async def handler(websocket):

    global shard_count, agent_count, node_count, sleep_time

    async def metrics_sender():
        await send_metrics(websocket)

    # 并行接收控制消息 + 发送指标
    async def control_receiver():
        global shard_count, agent_count, node_count, sleep_time
        async for message in websocket:
            try:
                msg = json.loads(message)
                if msg.get("type") == "control_update":
                    params = msg["params"]
                    shard_count = params.get("shardCount", shard_count)
                    agent_count = params.get("agentCount", agent_count)
                    node_count = params.get("nodeCount", node_count)
                    speed = params.get("evolutionSpeed", 1.0)
                    sleep_time = 1.0 / max(speed, 0.1)
                    print(
                        f"[Control] Updated: shards={shard_count}, "
                        f"agents={agent_count}, nodes={node_count}, "
                        f"speed={speed}/s"
                    )
            except json.JSONDecodeError:
                pass

    await asyncio.gather(
        metrics_sender(),
        control_receiver(),
    )


async def main():

    print(f"Sample WS server running on ws://localhost:{PORT}")
    print("Supports control_update messages from control_panel.js")

    async with websockets.serve(handler, "localhost", PORT):

        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
