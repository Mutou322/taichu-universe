# 太初知识宇宙 — 多 Agent 使用协议
## Taichu Knowledge Universe — Multi-Agent Access Protocol

> 任何 Agent / 子代理 / 外部工具在使用本知识库前，必须阅读此协议。
> 阅读时间：约 2 分钟。

---

## 1. 知识库概览

| 项目 | 值 |
|------|-----|
| 根目录 | `~/taichu/` |
| 词条数量 | 持续增长（核心词条 + 归档词条） |
| 存储引擎 | ChromaDB（语义向量）+ Markdown 文件（原始词条） |
| 搜索方式 | MemoryRuntime (ChromaDB 语义搜索) / 关键词降级 |
| 图谱引擎 | SemanticRuntime（双链关系图） |
| API 端口 | `http://127.0.0.1:8765`（REST） |
| 桌面客户端 | Tauri v2 桌面窗口（独立编译） |
| Web 客户端 | 浏览器访问 `http://localhost:8765` |

---

## 2. 目录结构

```
~/taichu/
├── ingest/              ← Layer 1: 文件摄入
│   ├── raw/             原始文件（所有上传文件落地于此）
│   ├── inbox/           待编译入口（doubao_manager 扫描此处）
│   ├── processed/       已处理文件
│   ├── failed/          处理失败
│   └── pipelines/       处理管道（markdown/pdf/image）
│       ├── __init__.py           ← dispatch(file, target)
│       ├── markdown_pipeline.py
│       ├── pdf_pipeline.py
│       └── image_pipeline.py
│
├── knowledge/           ← Layer 2: 语义层
│   ├── wiki/            编译后的知识词条（核心产出）
│   │   ├── index.md              ← 词条索引（所有词条入口）
│   │   ├── *.md                  知识词条
│   │   ├── architecture-*.md     架构文档
│   │   ├── session-*.md          会话日志
│   │   ├── study-*.md            源码分析报告
│   │   └── _archived/            归档词条
│   ├── graph/           图谱构建
│   │   ├── node.py              ← SemanticNode 数据类
│   │   ├── link_parser.py       双链解析
│   │   └── builder.py           ← GraphBuilder（build + suggest_relations）
│   ├── relations/        关系类型定义（8 种）
│   │   └── relation.py
│   └── wiki/compiler.py  WikiCompiler（.md → SemanticNode）
│
├── storage/             ← Layer 3: 存储层
│   ├── vector/
│   │   └── chroma_store.py      ← ChromaStore（封装 ChromaDB）
│   ├── embeddings/
│   │   └── embedder.py           ← Embedder（封装 sentence-transformers）
│   └── snapshots/
│       └── snapshot_manager.py   ← 快照（创建/回滚/列表）
│
├── runtime/             ← Layer 4: 运行时
│   ├── memory/
│   │   ├── api.py               ← MemoryRuntime（search/store/embed/delete）
│   │   └── hooks.py             事件钩子（→ EventBus）
│   ├── semantic/
│   │   └── runtime.py           ← SemanticRuntime（图谱查询）
│   ├── events/
│   │   ├── bus.py               ← EventBus（emit_sync / emit_async）
│   │   └── ws_bridge.py         ← WebSocket 映射
│   ├── graph/
│   │   └── api.py               ← GraphRuntime
│   └── agents/
│       └── base_agent.py        ← BaseAgent（think/recall/remember）
│
├── protocols/           ← Layer 5: 协议层
│   ├── memory/schema.py
│   ├── graph/schema.py
│   ├── agent/messages.py
│   └── websocket/events.py
│
├── interfaces/          ← 对外接口
│   ├── rest/server.py           ← FastAPI（端口 8766）
│   ├── websocket/server.py      ← WebSocket（端口 8767）
│   └── cli/main.py              ← CLI 接口
│
├── clients/             ← 客户端
│   ├── web/server.py            ← Web UI（FastAPI，端口 8765）
│   │   └── static/kb.js         ← Web 前端（forceAtlas2Based）
│   └── tauri/tauri-ui/
│       ├── frontend/            ← 桌面 UI 前端（barnesHut）
│       └── src-tauri/           ← Rust 后端（HTTP 代理）
│
├── config/
│   ├── paths.yaml               ← 统一路径配置
│   └── paths.py                 ← Python 读取器
│
├── tools/
│   ├── doubao_manager.py        ← 豆包编译入口
│   └── core/                    ← 多模态 ingest 核心
│       ├── ingest/              ← router.py / text/pdf/image
│       └── vision/              ← doubao_vision.py
│
└── docs/
    └── ARCHITECTURE.md          ← 架构设计文档
```

---

## 3. 搜索方式（按优先级）

### 方式 1：MemoryRuntime API（语义搜索，推荐）

```python
import sys
sys.path.insert(0, str(Path.home() / "taichu" / "config"))
sys.path.insert(0, str(Path.home() / "taichu"))
from paths import paths
from runtime.memory.api import MemoryRuntime

memory = MemoryRuntime()
results = memory.search("你的查询", top_k=5)
# 返回 [{"title": "...", "score": 0.85, "text": "..."}, ...]
```

### 方式 2：HTTP API（跨语言调用）

```bash
curl "http://127.0.0.1:8765/api/search?q=你的查询&limit=5"
```

### 方式 3：关键词搜索（无需向量引擎）

```bash
~/taichu/kb_search.sh "关键词"
# 纯 bash grep，所有 agent 可用
```

### 方式 4：知识图谱查询

```python
from runtime.semantic.runtime import SemanticRuntime
semantic = SemanticRuntime()
graph = semantic._ensure_graph()
# graph = {"nodes": [SemanticNode], "edges": [SemanticRelation]}
```

---

## 4. 写入方式

### 写词条

```python
from runtime.memory.api import MemoryRuntime
memory = MemoryRuntime()

# 存入一条知识
memory.store(
    doc_id="my-doc-id",
    text="知识内容",
    metadata={"source": "agent-xxx", "category": "study"},
)
```

### 上传文件到知识库

```python
from ingest.pipelines import dispatch

# 自动根据后缀选择管道
result_path = dispatch(Path("my_file.pdf"), Path("ingest/raw"))
```

### 编译待处理文件

```bash
cd ~/taichu && python3 tools/doubao_manager.py
```

---

## 5. 架构约束

| 禁令 | 说明 |
|------|------|
| **禁止直接读 ChromaDB** | 必须通过 MemoryRuntime API |
| **禁止硬编码路径** | 所有路径从 `config/paths.yaml` 读取 |
| **禁止跨层访问** | UI 层不能直接操作存储层 |
| **禁止写 `_archived/`** | 归档目录只读 |
| **禁止删 `index.md`** | 词条索引，所有 agent 依赖它 |

---

## 6. 常用命令速查

| 命令 | 用途 |
|------|------|
| `python3 ~/taichu/tools/doubao_manager.py` | 编译 inbox/ + raw/ 中的待处理文件 |
| `cd ~/taichu && python3 -c "from ingest.pipelines import dispatch; ..."` | 手动调度文件管道 |
| `cd ~/taichu/clients/web && python3 server.py 8765` | 启动 Web UI |
| `~/taichu/clients/tauri/tauri-ui/src-tauri/target/release/taichu-nebula` | 启动桌面窗口 |
| `cd ~/taichu && python3 -c "from storage.snapshots.snapshot_manager import SnapshotManager; ..."` | 创建/回滚快照 |
| `cd ~/taichu && python3 -c "from knowledge.graph.builder import GraphBuilder; ..."` | 图谱构建 + 关系推断 |
