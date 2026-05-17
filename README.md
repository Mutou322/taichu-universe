# 太初知识宇宙 — Taichu Knowledge Universe

> AI Runtime 原型 · 自演化知识图谱 · Canvas 2D/3D 星云可视化
> License: MIT

---



## 架构 Architecture

```
taichu/
├── runtime/                          # AI Runtime 引擎层
│   ├── agents/                       #   多 Agent 系统（5 种 Agent 类型）
│   ├── memory/api.py                 #   MemoryRuntime API（ChromaDB 封装）
│   ├── memory/session_memory.py      #   跨会话记忆管理器（Agent 记忆持久化）
│   ├── semantic/runtime.py           #   SemanticRuntime（图谱 + 语义引擎）
│   ├── retrieval/pipeline.py         #   6 阶段检索管道
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
│   ├── bootstrap.py                  #   统一运行时入口（延迟初始化工厂）
│   ├── phase9_main.py                #   主循环入口
│   └── phase9_archive_runtime.py     #   存档运行时
│
├── clients/                          # 客户端
│   ├── web/                          #   Web UI（FastAPI :8765）
│   │   ├── server.py                 #   主服务 + REST API + 内嵌 HTML 模板
│   │   └── static/
│   │       ├── kb.js                 #   前端核心逻辑（星云/搜索/设置/上传）
│   │       └── style.css             #   深色主题样式
│   └── tauri/                        #   Tauri 桌面端
│       └── tauri-ui/
│           ├── frontend/
│           │   ├── index.html        #   UI 模板
│           │   ├── kb.js             #   前端逻辑（2D + Three.js 3D 星云）
│           │   ├── kb_pipeline.js    #   管道追踪可视化（vis-network）
│           │   └── style.css
│           └── src-tauri/src/
│               ├── lib.rs            #   Tauri 命令注册 + 拖拽事件
│               ├── bridge.rs         #   HTTP 桥接到 Python API
│               ├── kb.rs             #   本地知识图谱构建器（文件系统）
│               ├── chroma.rs         #   ChromaDB 客户端（stub）
│               └── types.rs          #   Rust 数据结构
│
├── knowledge/                        # 知识库内容
│   ├── wiki/                         #   Markdown 知识词条
│   ├── wiki/_archived/               #   归档词条（只读）
│   ├── agents/                       #   Agent 专属文件（profile/personality/sessions）
│   ├── graph/                        #   图谱构建器
│   ├── relations/                    #   关系定义
│   ├── references/                   #   参考代码/下载文件（不纳入 git）
│   └── ...
│
├── config/                           # 统一配置（单源真理）
│   ├── paths.yaml                    #   路径配置
│   ├── models.yaml                   #   模型/Provider 配置
│   ├── paths.py                      #   路径读取器
│   └── models.py                     #   模型读取器
│
├── storage/                          # 持久化存储
│   ├── vector/chroma/                #   ChromaDB 向量数据库
│   ├── embeddings/                   #   Embedder
│   ├── snapshots/                    #   快照备份
│   └── raw/                          #   原始上传文件
│
├── ingest/pipelines/                 # 文件处理管道
├── tools/                            # 命令行工具集
│   ├── doubao_manager.py             #   豆包 LLM 管理/搜索/编译
│   ├── build_chromadb_index.py       #   构建/验证向量索引
│   ├── compile_openviking_archive.py #   归档编译器
│   ├── scripts/                      #   Wiki frontmatter 批量迁移等
│   └── core/kb/                      #   置信度评分、老化检测、Agent 文件管理
│
├── protocols/                        # 协议 Schema
│   ├── agent/messages.py             #   Agent 消息格式
│   ├── graph/schema.py               #   图谱 Schema
│   ├── memory/schema.py              #   记忆 Schema
│   └── websocket/events.py           #   WebSocket 事件类型
│
```

---

## 核心能力 Features

### 可视化 — Nebula 星云
| 引擎 | 描述 |
|------|------|
| **Canvas 2D** | 螺旋星系布局，差分旋转，悬停高亮 + 信息面板，缩放/平移 |
| **Three.js WebGL** | 3D 全息模式，轨道漫游，射线检测，粒子效果 |
| **设置面板** | 6 项画质控制（渲染引擎/视图模式/布局/节点数/转速/大小） |

### API 服务（:8765）
搜索：`GET /api/kb/search`（语义）· `GET /api/kb/ask`（RAG）· `GET /api/kb/graph`（图谱）
记忆：`POST /api/kb/memory`（保存）· `GET /api/kb/memory`（检索）· `POST /api/kb/memory/summarize`（压缩）
Agent：`POST /api/agents/register`（注册）· `POST /api/agents/heartbeat`（心跳）· `GET /api/agents`（列表）
Agent 文件：`GET/PUT /api/agents/{id}/profile` · `GET/PUT /api/agents/{id}/personality` · `GET /api/agents/{id}/sessions[/{date}]`
老化：`GET /api/kb/aging/report`（报告）· `GET /api/kb/aging/review`（重审）· `GET /api/kb/aging/archive-suggestions`（归档）
写入：`POST /upload`（上传文件）· `POST /api/kb/compile`（编译）
系统：`GET /health` · `GET /api/stats` · `GET /api/metrics` · `GET/POST /api/models[/switch]` · `WS /ws`

详细端点说明见 [`KB_ACCESS_PROTOCOL.md`](KB_ACCESS_PROTOCOL.md)。

### 模型管理
- 8 个内置 Provider：Ollama、火山引擎、阿里云、百度千帆、智谱、DeepSeek、Moonshot、SiliconFlow、OpenRouter、302.AI
- 5 个角色：compile（编译）、query（查询）、reasoning（推理）、embedding（嵌入）、vision（视觉）
- Web UI 设置页可视化切换，自动回写 `config/models.yaml`
- 语言设置：中文 / English，localStorage 持久化

### Runtime 引擎
- **6 阶段检索管道**：查询解析 → 向量搜索 → 图谱扩展 → 本体过滤 → 重排序 → 上下文构建
- **GBrain 语义智能**：关系推断、聚类检测、语义重力、本体构建
- **GEP 自演化**：基因组 → 变异 → 沙盒实验 → 适应度评估闭环
- **多 Agent 系统**：RetrievalAgent、GraphAgent、MemoryAgent、SynthesizerAgent、PlannerAgent
- **Semantic Attention**：全局注意力场、路由、传播、热点聚类、涌现生态
- **事件总线**：10 种内部事件 → WebSocket 广播
- **知识老化检测**：三因子评分（时间/频率/置信度），四级分类（active/notice/aging/stale），frontmatter 自动标记
- **跨会话记忆**：Agent 会话记忆持久化到 ChromaDB，所有 Agent 通过统一 REST API 读写，重启不丢失

### 知识摄取
- 20+ 文件格式支持（md/pdf/docx/pptx/html/txt/csv/xlsx/epub/图片/代码）
- 自动去重（hash 校验）、格式转换、wiki 编译
- 归档层（raw/manifest/provenance/fingerprint 完整追溯）
- 向量索引（ChromaDB）+ 图谱索引（GraphBuilder）

---

## 客户端对比

| 特性 | Web UI（浏览器） | Tauri 桌面端 |
|------|:-:|:-:|
| 渲染引擎 | Canvas 2D / Three.js 3D | Canvas 2D / Three.js 3D |
| 星云布局 | 螺旋星系 / 圆形 | 螺旋星系 / 圆形 |
| 信息面板 | 右上角浮动面板 | 右侧浮动面板 |
| 节点搜索 | 顶部搜索栏 | 顶部搜索栏 |
| 3D 模式 | 设置页切换 | 首页 3D 复选框 |
| 上传方式 | 浏览器拖拽/选择 | 系统原生拖拽 + IPC |
| 模型切换 | 设置页 | 设置页 |
| 语言切换 | 设置页 | 设置页 |
| 文件上传 | HTTP multipart | Tauri IPC + HTTP 转发 |
| WS 实时推送 | 支持（未启用） | 支持（已启用） |

---

## 快速开始 Quick Start

```bash
# 1. 安装依赖
pip install fastapi uvicorn chromadb sentence-transformers httpx PyYAML scikit-learn

# 2. 启动 Web 服务
cd ~/taichu && python3 clients/web/server.py 8765
# → http://localhost:8765（Web UI） / http://127.0.0.1:8765（API）

# 3. （可选）Phase 9 主循环
python3 runtime/phase9_main.py
```

---

## 文档索引

| 文档 | 用途 |
|------|------|
| `KB_ACCESS_PROTOCOL.md` | 多 Agent 使用协议（外部 Agent/工具 必读）|
| `knowledge/wiki/index.md` | 知识库索引 |
| `knowledge/wiki/` | 全部知识词条 |
| `config/paths.yaml` | 统一路径配置（单源真理） |
| `config/models.yaml` | 模型/Provider 配置 |
| `knowledge/references/` | 第三方参考代码/下载文件（不纳入 git） |

---

## 版本

v3.4.0 — 2026-05-16
- Agent 专属文件系统：注册时自动创建 knowledge/agents/{agent_id}/ 目录，含 profile/personality/sessions
- Agent 注册与心跳检测：注册制 + 60s 超时判定在线/离线
- Agent profile/personality/sessions REST API（7 个端点）
- 知识老化检测系统：三因子评分引擎 + frontmatter 自动标记 + 6 个 API 端点
- 跨会话记忆持久化：Agent 记忆存 ChromaDB 重启不丢失，所有 Agent 统一 REST API
- Wiki 文章规范化：423 篇文章统一 YAML frontmatter（article/session/note 三类）
- Confidence 置信度追踪：5 因子评分引擎，搜索可置信度过滤，UI 彩色 badge
- 自研星云渲染引擎（Canvas 2D + Three.js 3D）
- 模型切换 UI（8+ Provider 可视化切换）
- 中英双语界面
- 画质/性能调节面板
- Tauri 桌面端文件原生拖拽上传
- 全部 pre-commit hooks 通过
