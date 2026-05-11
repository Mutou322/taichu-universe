# taichu-universe

> AI Runtime Prototype — 认知基础设施 · 五层架构知识宇宙  
> Not a RAG demo, not a script — an AI Runtime that can evolve.

五层分离的 AI 运行时系统。具备语义图谱、向量搜索、实时事件总线、多 Agent 运行时和多模态文件管道。不是知识库脚本，不是 RAG Demo。

```bash
pip install fastapi uvicorn chromadb sentence-transformers httpx PyYAML
cd clients/web && python3 server.py 8765
# → http://localhost:8765
```

---

## 架构 Architecture

```
ingest/     文件 → 内容 (MD/PDF/Image)
knowledge/  语义结构 (图谱 + 关系自动发现)
storage/    存储索引 (ChromaDB + 快照)
runtime/    运行时 (EventBus + Agent)
protocols/  数据契约 (Schema)
```

## 能力 Features

- 多模态文件管道 (15 种格式) Multi-modal ingestion
- 语义图谱 + 关系自动发现 Semantic graph + auto relation discovery
- 向量语义搜索 Vector search (ChromaDB semantic index)
- 实时事件推送 Real-time event bus (WebSocket broadcast)
- 快照回滚 Snapshot backup/restore
- Web UI (:8765) + Tauri 桌面端 Desktop client
- Agent API MemoryRuntime.search() / store()

## 客户端 Client

| 平台 | 引擎 | 图谱 |
|------|------|------|
| Web UI (浏览器) | forceAtlas2Based | Top 150 nodes |
| Tauri 桌面端 | barnesHut | Full 565 nodes |

## 依赖 Dependencies

```bash
# 必需 Required
pip install fastapi uvicorn chromadb sentence-transformers httpx PyYAML

# 可选 Optional
pip install markitdown       # PDF/Office 解析
pip install pymupdf4llm      # 更好的 PDF 解析
```

## 版本 Version

v0.2.0 — 2026-05-12  
License: MIT
