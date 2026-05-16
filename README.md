# 太初知识宇宙 — Taichu Knowledge Universe

> AI Runtime 原型 · 自演化知识图谱 · Canvas 2D/3D 星云可视化
> AI Runtime Prototype · Self-Evolving Knowledge Graph · Canvas 2D/3D Nebula Visualization
>
> **文档**: [`docs/REFERENCE.md`](docs/REFERENCE.md)（完整参考） · [`KB_ACCESS_PROTOCOL.md`](KB_ACCESS_PROTOCOL.md)（API 协议）
> **License**: MIT

---

## 架构 Architecture

```
taichu/
├── runtime/                          # AI Runtime 引擎层
│   ├── agents/                       #   多 Agent 系统（5 种 Agent 类型）
│   ├── memory/                       #   MemoryRuntime API + 跨会话记忆
│   ├── semantic/                     #   SemanticRuntime（图谱 + 语义引擎）
│   ├── retrieval/                    #   6 阶段检索管道
│   ├── gbrain/                       #   语义智能中枢（关系推断/聚类/重力/本体）
│   ├── attention/                    #   Semantic Attention（14 模块）
│   ├── evolution/                    #   GEP 自演化（基因组/变异/沙盒/适应度）
│   ├── planning/                     #   DAG 工作流（任务分解/执行/协作）
│   ├── scheduler/                    #   自适应调度器
│   ├── capabilities/                 #   能力路由系统
│   ├── specialization/               #   Agent 特化画像
│   ├── events/                       #   事件总线 + WebSocket 桥接
│   ├── metrics/                      #   可观测性（指标总线/计时器/追踪/计数器）
│   ├── ingestion/                    #   持续知识摄取
│   ├── archive/                      #   文件存档层
│   ├── bootstrap.py                  #   统一运行时入口
│   ├── phase9_main.py                #   主循环入口
│   └── phase9_archive_runtime.py     #   存档运行时
│
├── clients/                          # 客户端 Clients
│   ├── web/                          #   Web UI（FastAPI :8765）
│   │   └── static/                   #   kb.js, style.css
│   └── tauri/                        #   Tauri 桌面端 Desktop App
│       └── tauri-ui/
│           ├── frontend/             #   HTML + JS + CSS
│           └── src-tauri/src/        #   Rust: lib.rs, bridge.rs, kb.rs, types.rs
│
├── knowledge/                        # 知识库 Knowledge Base
│   ├── wiki/                         #   Markdown 知识词条
│   ├── wiki/_archived/               #   归档词条（只读）
│   ├── agents/                       #   Agent 专属文件（profile/personality/sessions）
│   ├── graph/                        #   图谱构建器
│   ├── relations/                    #   关系定义
│   └── references/                   #   参考代码/下载文件（不纳入 git）
│
├── config/                           # 统一配置 Configuration
├── storage/                          # 持久化存储 Persistence
│   └── vector/chroma/                #   ChromaDB 向量数据库
│
├── ingest/pipelines/                 # 文件处理管道 Ingestion Pipelines
├── tools/                            # 命令行工具集 CLI Tools
│   └── core/kb/                      #   置信度评分、老化检测、Agent 文件管理
├── protocols/                        # 协议 Schema Protocols
├── tests/                            # 测试 Tests
├── benchmarks/                       # 性能基准 Benchmarks
└── docs/                             # 文档 Documentation
```

---

## 快速开始 Quick Start

```bash
# 1. 安装依赖 Install dependencies
pip install -r requirements.txt

# 2. 启动 Web 服务 Start Web server
cd ~/taichu && python3 clients/web/server.py 8765
# → http://localhost:8765（Web UI） / http://127.0.0.1:8765（API）

# 3. （可选）Phase 9 主循环 Optional: main loop
python3 runtime/phase9_main.py
```

---

## 核心能力 Features

### 可视化 — Nebula Visualization

| 引擎 Engine | 描述 Description |
|-------------|------------------|
| **Canvas 2D** | 螺旋星系布局，悬停高亮，缩放/平移。Spiral galaxy, hover highlight, zoom/pan. |
| **Three.js 3D** | 全息模式，轨道漫游，粒子效果。Holographic mode, orbital camera, particle effects. |
| **设置面板 Settings** | 6 项画质控制（渲染引擎/视图/布局/节点数/转速/大小）。 |

### API 服务 API Server（:8765）

| 分类 Category | 端点 Endpoints |
|---------------|----------------|
| **搜索 Search** | `GET /api/kb/search`（语义检索）· `GET /api/kb/ask`（RAG）· `GET /api/kb/graph`（图谱） |
| **记忆 Memory** | `POST /api/kb/memory`（保存）· `GET /api/kb/memory`（检索）· `POST /api/kb/memory/summarize`（压缩） |
| **Agent** | `POST /api/agents/register` · `POST /api/agents/heartbeat` · `GET /api/agents` |
| **Agent 文件 Files** | `GET/PUT /api/agents/{id}/profile` · `GET/PUT /api/agents/{id}/personality` · `GET /api/agents/{id}/sessions` |
| **老化检测 Aging** | `GET /api/kb/aging/report` · `GET /api/kb/aging/review` · `GET /api/kb/aging/archive-suggestions` |
| **写入 Write** | `POST /upload`（文件上传）· `POST /api/kb/compile`（编译） |
| **系统 System** | `GET /health` · `GET /api/stats` · `GET /api/metrics` · `WS /ws` |

详细端点说明见 Detailed API reference: [`KB_ACCESS_PROTOCOL.md`](KB_ACCESS_PROTOCOL.md) / [`docs/REFERENCE.md`](docs/REFERENCE.md#3-完整-api-参考)

### 模型管理 Model Management

- **8+ Provider**: Ollama, 火山引擎, 阿里云, 百度千帆, 智谱, DeepSeek, Moonshot, SiliconFlow, OpenRouter, 302.AI
- **5 角色 Roles**: compile（编译）, query（查询）, reasoning（推理）, embedding（嵌入）, vision（视觉）
- Web UI 可视化切换，自动回写配置文件 Visual switching, auto-save to `config/models.yaml`
- 中英双语界面切换 Chinese/English language toggle

### Runtime 引擎 Runtime Engine

| 模块 Module | 说明 Description |
|-------------|------------------|
| **6 阶段检索** 6-Stage Retrieval | 查询解析 → 向量搜索 → 图谱扩展 → 本体过滤 → 重排序 → 上下文构建 |
| **GBrain 语义智能** | 关系推断、聚类检测、语义重力、本体构建 Relation inference, clustering, gravity, ontology |
| **GEP 自演化** Evolution | 基因组 → 变异 → 沙盒实验 → 适应度评估闭环 Genome → mutation → sandbox → fitness |
| **多 Agent 系统** | RetrievalAgent, GraphAgent, MemoryAgent, SynthesizerAgent, PlannerAgent |
| **Semantic Attention** | 全局注意力场、路由、传播、热点聚类、涌现生态 Global field, routing, clustering |
| **事件总线 Event Bus** | 10 种内部事件 → WebSocket 广播 10 internal events → WS broadcast |
| **知识老化 Aging** | 三因子评分（时间/频率/置信度）Time/Frequency/Confidence scoring |
| **跨会话记忆 Memory** | Agent 记忆持久化到 ChromaDB，重启不丢失 Persistent ChromaDB memory |

### 知识摄取 Ingestion

- **20+ 格式支持 Formats**: md/pdf/docx/pptx/html/txt/csv/xlsx/epub/图片/代码
- 自动去重（hash 校验）、格式转换、wiki 编译 Dedup, conversion, compilation
- 归档追溯: raw/manifest/provenance/fingerprint 完整追溯 Full audit trail
- 双索引: ChromaDB 向量索引 + GraphBuilder 图谱索引 Vector + Graph index

---

## 客户端对比 Client Comparison

| 特性 Feature | Web UI | Tauri 桌面端 Desktop |
|--------------|:------:|:--------------------:|
| 渲染引擎 Renderer | Canvas 2D / Three.js 3D | Canvas 2D / Three.js 3D |
| 上传方式 Upload | 浏览器拖拽 Browser drag | 系统原生拖拽 Native drag |
| WS 推送 Push | 支持 Supported | 已启用 Enabled |
| 模型切换 Model Switch | 设置页 Settings | 设置页 Settings |
| 语言切换 Language | 设置页 Settings | 设置页 Settings |

---

## 文档索引 Document Index

| 文档 Document | 用途 Purpose |
|---------------|--------------|
| `KB_ACCESS_PROTOCOL.md` | 多 Agent 使用协议 API protocol for external Agents |
| `docs/REFERENCE.md` | 完整参考手册 Full reference manual |
| `config/paths.yaml` | 统一路径配置 Path configuration |
| `config/models.yaml` | 模型/Provider 配置 Model configuration |

---

## 版本 Version

**v3.4.0** — 2026-05-16

- Agent 专属文件系统 Agent file system（profile/personality/sessions）
- 知识老化检测系统 Knowledge aging detection（3-factor scoring）
- 跨会话记忆持久化 Cross-session memory persistence（ChromaDB）
- 中英双语界面 Bilingual UI（中文/English）
- Tauri 桌面端原生拖拽上传 Native drag-and-drop upload
- 自研星云渲染引擎 Custom nebula rendering（Canvas 2D + Three.js 3D）
