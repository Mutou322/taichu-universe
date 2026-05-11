"""Taichu Knowledge Web UI (FastAPI) — 基于新 taichu 架构
提供 HTML 页面 + API 端点，适配旧版 Web UI 前端 JS 的调用格式。
"""

import json
import os
import re
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path.home() / "taichu" / "config"))
sys.path.insert(0, str(Path.home() / "taichu"))

# 使用 taichu_venv Python 环境（含 sentence_transformers 等）
_VENV = Path.home() / "taichu_venv" / "lib" / f"python3.{sys.version_info.minor}" / "site-packages"
if _VENV.exists():
    sys.path.insert(0, str(_VENV))

from paths import paths

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ── 静态文件 ──
STATIC_DIR = Path(__file__).parent / "static"

# ── 运行时 ──
sys.path.insert(0, str(Path.home() / "taichu"))
from runtime.memory.api import MemoryRuntime
memory = MemoryRuntime()

from runtime.semantic.runtime import SemanticRuntime
semantic = SemanticRuntime()


SUPPORTED_EXT = {".pdf", ".docx", ".pptx", ".html", ".htm", ".txt",
                 ".csv", ".xlsx", ".json", ".xml", ".rtf", ".epub",
                 ".md", ".markdown",
                 ".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp",
                 ".py", ".js", ".ts", ".yaml", ".toml"}


PAGE_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Taichu Knowledge</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/vis-network@9.1.6/dist/vis-network.min.js"></script>
<link rel="stylesheet" href="/static/style.css">
</head>
<body>
<div class="topbar">
  <div class="topbar-logo"><span class="logo-dot"></span>Taichu</div>
  <div class="topbar-item active" data-tab="overview" onclick="switchTab('overview')"><span class="icon">📖</span> 概览</div>
  <div class="topbar-item" data-tab="entries" onclick="switchTab('entries')"><span class="icon">📄</span> 词条</div>
  <div class="topbar-item" data-tab="nebula" onclick="switchTab('nebula')"><span class="icon">🌌</span> 星云</div>
  <div class="topbar-item" data-tab="search" onclick="switchTab('search')"><span class="icon">🔍</span> 搜索</div>
  <div class="topbar-item" data-tab="links" onclick="switchTab('links')"><span class="icon">🔗</span> 链接</div>
  <div class="topbar-spacer"></div>
  <div class="topbar-item" data-tab="settings" onclick="switchTab('settings')"><span class="icon">⚙</span> 设置</div>
</div>
<div class="main">
  <div class="panel-section" id="section-overview">
    <h2>知识库</h2>
    <div class="subtitle"><code>~/taichu/</code> — 太初知识宇宙</div>
    <div class="stats-row" id="stats-bar"></div>

    <div class="upload-inline">
      <div class="upload-inline-header">✦ 上传文件</div>
      <div class="upload-zone" id="dropzone">
        <div class="icon">✦</div>
        <div class="text">拖放文件到此处，或点击选择</div>
        <div class="hint">.md → 直接发布 · 其他格式 → raw/ + 豆包编译</div>
        <input type="file" id="file-input" accept=".md,.pdf,.docx,.pptx,.html,.htm,.txt,.csv,.xlsx,.epub,.png,.jpg,.jpeg,.webp,.gif,.bmp,.py,.js,.ts,.yaml,.toml" multiple>
      </div>
      <div id="result"></div>
      <div class="panels-row" style="margin-top:12px;">
        <div class="panel">
          <div class="panel-header">📋 待处理文件 <span id="pending-badge"></span></div>
          <div class="panel-body" id="pending-panel" style="max-height:240px;overflow-y:auto;">
            <div class="empty">✦ 没有待处理文件</div>
          </div>
          <div style="padding:8px 14px 12px;display:flex;gap:8px;">
            <button id="compile-btn" onclick="triggerCompile()" style="flex:1;padding:7px 0;background:var(--gold);border:none;border-radius:5px;color:#fff;font-size:12px;cursor:pointer;font-weight:500;">⚡ 编译待处理文件</button>
            <button onclick="refreshPending()" style="padding:7px 12px;background:var(--card);border:1px solid var(--border);border-radius:5px;color:var(--sec);font-size:12px;cursor:pointer;">⟳</button>
          </div>
        </div>
      </div>
    </div>

    <div class="actions">
      <button onclick="refreshStats();refreshPending();">⟳ 刷新</button>
    </div>
  </div>

  <div class="panel-section hidden" id="section-entries">
    <h2>词条</h2>
    <div class="subtitle">全部词条列表</div>
    <div id="wiki-panel"></div>
  </div>

  <div class="panel-section hidden" id="section-nebula">
    <div class="nebula-card">
      <div class="nebula-header">🌌 知识星云</div>
      <div style="display:flex;gap:8px;padding:8px 16px;border-bottom:1px solid var(--border);align-items:center;">
        <input id="nebula-search-input" type="text" placeholder="输入节点名称跳转..." style="flex:1;padding:8px 12px;background:var(--surface);border:1px solid var(--border);border-radius:4px;color:var(--text-primary);font-size:13px;outline:none;" onkeydown="if(event.key==='Enter')doNebulaSearch()">
        <button onclick="doNebulaSearch()" style="padding:8px 14px;background:var(--accent);border:none;border-radius:4px;color:#fff;font-size:13px;cursor:pointer;">跳转</button>
      </div>
      <div style="position:relative;">
        <div id="kb-graph" style="height:440px;background:#0a0a1a;"></div>
        <div id="kb-tooltip" style="position:absolute;display:none;background:var(--surface-card);border:1px solid var(--accent);border-radius:var(--radius-sm);padding:10px 14px;max-width:300px;max-height:180px;overflow-y:auto;z-index:1000;box-shadow:0 4px 12px rgba(0,0,0,0.5);pointer-events:none;color:var(--text-primary);font-size:13px;"></div>
      </div>
      <div class="nebula-hint">拖拽移动 · 滚轮缩放 · 悬停查看摘要 · 双击聚焦</div>
    </div>
  </div>

  <div class="panel-section hidden" id="section-search">
    <div class="nebula-card">
      <div class="nebula-header">🔍 语义搜索 <span style="font-weight:400;font-size:11px;color:var(--dim);">MemoryRuntime + ChromaDB</span></div>
      <div style="padding:14px;">
        <div style="display:flex;gap:8px;margin-bottom:10px;">
          <input id="search-input" type="text" placeholder="输入搜索词或问题..." style="flex:1;padding:9px 12px;background:var(--surface);border:1px solid var(--border);border-radius:5px;color:var(--text);font-size:13px;outline:none;" onkeydown="if(event.key==='Enter')doSearch()">
          <button onclick="doSearch()" style="padding:9px 18px;background:var(--gold);border:none;border-radius:5px;color:#fff;font-size:13px;cursor:pointer;font-weight:500;">搜索</button>
        </div>
        <div style="display:flex;gap:6px;margin-bottom:14px;">
          <button id="mode-search" onclick="setSearchMode('search')" style="padding:5px 12px;border-radius:4px;border:1px solid var(--border);background:var(--gold);color:#fff;font-size:11px;cursor:pointer;">🔎 语义检索</button>
          <button id="mode-ask" onclick="setSearchMode('ask')" style="padding:5px 12px;border-radius:4px;border:1px solid var(--border);background:var(--surface);color:var(--dim);font-size:11px;cursor:pointer;">💬 AI 问答</button>
        </div>
        <div id="search-result" style="font-size:12px;line-height:1.6;color:var(--sec);min-height:50px;">
          <div style="color:var(--dim);font-style:italic;">输入关键词进行语义搜索，或切换至"AI 问答"模式获取回答。</div>
        </div>
      </div>
    </div>
  </div>

  <div class="panel-section hidden" id="section-links">
    <div class="nebula-card">
      <div class="nebula-header">🔗 链接关系</div>
      <div style="padding:8px 14px 14px;" id="kb-link-table">
        <div style="color:var(--dim);font-size:11px;font-style:italic;padding:6px 0;">加载中...</div>
      </div>
    </div>
  </div>

  <div class="panel-section hidden" id="section-settings">
    <div class="nebula-card">
      <div class="nebula-header">⚙ 设置</div>
      <div style="padding:16px;font-size:12px;color:var(--sec);">
        <div style="margin-bottom:4px;">知识库路径：<code style="color:var(--gold);">~/taichu/</code></div>
        <div style="margin-bottom:4px;">API 服务：<code style="color:var(--green);">http://127.0.0.1:8765</code></div>
        <div style="margin-bottom:4px;">搜索引擎：<code style="color:var(--sec);">MemoryRuntime + ChromaDB</code></div>
        <div id="settings-stats" style="margin-top:12px;border-top:1px solid var(--border);padding-top:12px;">
          <div style="color:var(--dim);font-style:italic;">加载中...</div>
        </div>
      </div>
    </div>
  </div>
</div>
<script src="/static/kb.js"></script>
</body>
</html>"""


# ── FastAPI app ──

app = FastAPI(title="太初知识宇宙 Web UI", version="0.3.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# 构建可序列化的图谱数据（兼容 vis-network json 格式）
def _build_graph_json() -> dict:
    """返回 {nodes: [{id, label, value, summary, links}, ...], edges: [{from, to}, ...]}"""
    graph = semantic._ensure_graph()
    nodes = []
    for n in graph["nodes"]:
        nodes.append({
            "id": n.id,
            "label": n.title,
            "value": max(1, len(n.links)),
            "summary": n.summary or (n.content[:200] if n.content else ""),
            "links": n.links,
        })
    edges = []
    for e in graph["edges"]:
        edges.append({"from": e.source, "to": e.target})
    return {"nodes": nodes, "edges": edges, "total_nodes": len(nodes)}


def _scan_wiki_files():
    """扫描 wiki 目录，返回 {wiki_files, archived_files, wiki_count, archived_count}"""
    wiki_dir = paths.wiki_dir
    archived_dir = wiki_dir / "_archived"

    wiki_files = sorted([f.stem for f in wiki_dir.glob("*.md") if f.stem != "index"]) if wiki_dir.exists() else []
    archived_files = sorted([
        str(f.relative_to(wiki_dir))
        for f in archived_dir.rglob("*.md")
        if f.stem != "index"
    ]) if archived_dir.exists() else []

    return {
        "wiki_files": wiki_files,
        "archived_files": archived_files,
        "wiki_count": len(wiki_files),
        "archived_count": len(archived_files),
    }


# ── 主页 ──

@app.get("/", response_class=HTMLResponse)
async def index():
    return PAGE_HTML


# ── 统计 ──

@app.get("/api/stats")
async def api_stats():
    scanned = _scan_wiki_files()
    # ChromaDB 信息
    chroma_ok = False
    chroma_count = 0
    chroma_collections = []
    try:
        store = memory._get_store()
        chroma_ok = True
        chroma_count = store.count
        try:
            chroma_collections = [c.name for c in store.client.list_collections()]
        except:
            chroma_collections = ["taichu_memory"]
    except Exception:
        chroma_ok = False

    return {
        "wiki_count": scanned["wiki_count"],
        "archived_count": scanned["archived_count"],
        "total_count": scanned["wiki_count"] + scanned["archived_count"],
        "wiki_articles": scanned["wiki_files"],
        "archived_articles": scanned["archived_files"],
        "chroma_available": chroma_ok,
        "chroma_count": chroma_count,
        "chroma_collections": chroma_collections,
    }


# ── 图谱 ──

@app.get("/api/kb/graph")
async def kb_graph(limit: int = 150, expand: str = ""):
    graph_data = _build_graph_json()

    if expand:
        # 单节点扩展模式
        expand_nodes = set(expand.split(","))
        connected_edges = [
            e for e in graph_data["edges"]
            if e["from"] in expand_nodes or e["to"] in expand_nodes
        ]
        neighbor_ids = set()
        for e in connected_edges:
            neighbor_ids.add(e["from"])
            neighbor_ids.add(e["to"])
        filtered_nodes = [n for n in graph_data["nodes"] if n["id"] in neighbor_ids]
        return {
            "nodes": filtered_nodes,
            "edges": connected_edges,
            "total_nodes": graph_data["total_nodes"],
            "mode": "expand",
        }

    if limit == 0:
        # 全量数据（桌面端专用）
        return {
            "nodes": graph_data["nodes"],
            "edges": graph_data["edges"],
            "total_nodes": graph_data["total_nodes"],
            "mode": "full",
        }

    # 按 degree 排序取 top
    degree = {}
    for e in graph_data["edges"]:
        degree[e["from"]] = degree.get(e["from"], 0) + 1
        degree[e["to"]] = degree.get(e["to"], 0) + 1

    top_ids = set(sorted(degree, key=degree.get, reverse=True)[:limit])
    return {
        "nodes": [n for n in graph_data["nodes"] if n["id"] in top_ids],
        "edges": [e for e in graph_data["edges"]
                  if e["from"] in top_ids and e["to"] in top_ids],
        "total_nodes": graph_data["total_nodes"],
        "mode": "core",
    }


# ── 搜索（兼容旧前端格式）──

@app.get("/api/kb/search")
async def kb_search(q: str = "", mode: str = "search"):
    if not q:
        return {"results": [], "error": "请输入搜索词"}

    try:
        results = memory.search(q, top_k=5)
        if results:
            lines = [
                f"  {i+1}. [[{r['title']}]] (score: {r['score']:.4f})"
                for i, r in enumerate(results)
            ]
            output = f"Semantic search: {q}\n\n  Engine: MemoryRuntime\n  Results: {len(results)}\n\n" + "\n".join(lines)
            return {"query": q, "mode": mode, "output": output, "engine": "memory_runtime"}
    except Exception as e:
        return {"query": q, "mode": mode, "output": "", "error": str(e)}

    return {"query": q, "mode": mode, "output": "(无匹配结果)", "engine": "memory_runtime"}


@app.get("/api/kb/ask")
async def kb_ask(q: str = ""):
    if not q:
        return {"error": "请输入问题"}
    # 先搜到相关内容，再做 LLM 问答（暂用简单 RAG）
    try:
        results = memory.search(q, top_k=3)
        context = "\n".join([r.get("text", "")[:500] for r in results])
        answer = f"找到 {len(results)} 条相关结果。\n\n"
        for i, r in enumerate(results):
            preview = r.get("text", "")[:200]
            answer += f"{i+1}. [[{r['title']}]] — {preview}\n"
        return {"query": q, "raw_output": answer}
    except Exception as e:
        return {"error": str(e)}


# ── 待处理文件 ──

@app.get("/api/kb/pending")
async def kb_pending():
    inbox_dir = paths.inbox_dir
    files = []
    if inbox_dir.exists():
        for f in sorted(inbox_dir.iterdir()):
            if f.is_dir() or f.suffix == ".md":
                continue
            files.append({
                "name": f.name,
                "size": f.stat().st_size,
                "modified": f.stat().st_mtime,
            })
    return {"pending": files, "count": len(files)}


@app.post("/api/kb/pending/delete")
async def kb_pending_delete(request: Request):
    body = await request.json()
    filename = body.get("filename", "").strip()
    if not filename:
        return {"ok": False, "error": "请指定文件名"}
    if "/" in filename or ".." in filename:
        return {"ok": False, "error": "非法文件名"}
    raw_target = paths.raw_dir / filename
    inbox_target = paths.inbox_dir / filename
    deleted = 0
    if inbox_target.exists():
        inbox_target.unlink()
        deleted += 1
    if raw_target.exists():
        raw_target.unlink()
        deleted += 1
    return {"ok": deleted > 0, "deleted": deleted, "note": f"已删除 {filename}"}


@app.post("/api/kb/compile")
async def kb_compile():
    doubao = paths.get("tools") / "doubao_manager.py"
    if not doubao.exists():
        return {"ok": False, "error": "doubao_manager.py 不存在"}
    try:
        result = subprocess.run(
            [sys.executable, str(doubao)],
            capture_output=True, text=True, timeout=300,
            cwd=str(paths.root),
        )
        output = result.stdout.strip()
        converted = 0
        if "CONVERTED:" in output:
            converted = int(output.split("CONVERTED:")[-1].split("\n")[0])
        # 编译完成后刷新语义图谱
        if result.returncode == 0 and converted > 0:
            semantic.refresh()
        return {
            "ok": result.returncode == 0,
            "converted": converted,
            "output": output,
            "error": result.stderr.strip() if result.returncode != 0 else "",
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "编译超时(300s)"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ── 上传 ──

@app.post("/upload")
async def upload(files: list[UploadFile] = File(...)):
    raw_dir = paths.raw_dir
    inbox_dir = paths.inbox_dir
    wiki_dir = paths.wiki_dir
    raw_dir.mkdir(parents=True, exist_ok=True)
    inbox_dir.mkdir(parents=True, exist_ok=True)
    wiki_dir.mkdir(parents=True, exist_ok=True)

    uploaded_md, uploaded_other = 0, 0
    for f in files:
        ext = Path(f.filename).suffix.lower()
        if ext not in SUPPORTED_EXT:
            continue
        content = await f.read()
        raw_target = raw_dir / f.filename
        with open(raw_target, "wb") as wf:
            wf.write(content)
        if ext == ".md":
            wiki_target = wiki_dir / f.filename
            with open(wiki_target, "wb") as wf:
                wf.write(content)
            uploaded_md += 1
        else:
            inbox_target = inbox_dir / f.filename
            with open(inbox_target, "wb") as wf:
                wf.write(content)
            uploaded_other += 1

    parts = []
    if uploaded_md:
        parts.append(f"{uploaded_md} 个 .md 已发布到 wiki/")
    if uploaded_other:
        parts.append(f"{uploaded_other} 个文件待编译，点击「编译待处理文件」按钮")
    return {
        "ok": True,
        "md_count": uploaded_md,
        "other_count": uploaded_other,
        "compiled": False,
        "note": "；".join(parts) if parts else "没有文件被上传",
    }


@app.post("/compile")
async def compile_check():
    return {"ok": True, "count": 0, "pending": [], "note": "已弃用，请使用上传面板自动编译"}


@app.get("/health")
async def health():
    return {"status": "ok"}


# ── 入口 ──

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Taichu KB Web UI (FastAPI)")
    parser.add_argument("port", nargs="?", type=int, default=8765)
    parser.add_argument("--bind", default="0.0.0.0")
    args = parser.parse_args()
    print(f"太初知识宇宙 Web UI — http://localhost:{args.port}")
    print(f"  知识库: {paths.root}")
    print(f"  API:    /api/stats /api/kb/graph /api/kb/search /api/kb/pending")
    uvicorn.run(app, host=args.bind, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
