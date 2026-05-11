"""REST 接口服务器 — 供 Tauri/浏览器/其他客户端调用

启动:
    python3 interfaces/rest/server.py
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path.home() / "taichu"))

# 使用 taichu_venv Python 环境（含 sentence_transformers）
_VENV = Path.home() / "taichu_venv" / "lib" / f"python3.{sys.version_info.minor}" / "site-packages"
if _VENV.exists():
    sys.path.insert(0, str(_VENV))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="太初知识宇宙 API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 各个 API 路由 ──

# 记忆搜索
from runtime.memory.api import memory as _memory

@app.get("/api/search")
def search(q: str, limit: int = 10):
    return _memory.search(q, top_k=limit)


# 图谱
from runtime.semantic.runtime import semantic as _semantic

@app.get("/api/kb/graph")
def kb_graph(limit: int = 200):
    graph = _semantic._ensure_graph()
    nodes = []
    edges = []
    for n in graph["nodes"][:limit]:
        nodes.append({"id": n.id, "label": n.title, "category": n.category})
    for e in graph["edges"]:
        edges.append({"from": e.source, "to": e.target, "relation_type": e.relation_type})
    return {"nodes": nodes, "edges": edges}


# 状态
@app.get("/api/stats")
def stats():
    return {
        "wiki_count": _semantic.node_count,
        "link_count": _semantic.edge_count,
        "chroma_available": True,
    }


# 健康检查
@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8766)
