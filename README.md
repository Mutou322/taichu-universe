[English](README.en.md) · **中文**

# 太初知识宇宙 — Taichu Knowledge Universe

> AI Runtime 原型 · 自演化知识图谱 · Canvas 2D/3D 星云可视化
> License: MIT
>
> 完整参考手册 → [`docs/REFERENCE.md`](docs/REFERENCE.md)

---

## 架构

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
├── clients/                          # 客户端
│   ├── web/                          #   Web UI（FastAPI :8765）
│   │   └── static/                   #   kb.js, style.css
│   └── tauri/                        #   Tauri 桌面端
│       └── tauri-ui/
│           ├── frontend/             #   HTML + JS + CSS
│           └── src-tauri/src/        #   Rust: lib.rs, bridge.rs, kb.rs, types.rs
│
├── knowledge/                        # 知识库
│   ├── wiki/                         #   Markdown 知识词条
│   ├── wiki/_archived/               #   归档词条（只读）
│   ├── agents/                       #   Agent 专属文件
│   ├── graph/                        #   图谱构建器
│   ├── relations/                    #   关系定义
│   └── references/                   #   参考文件（不纳入 git）
│
├── config/                           # 统一配置
├── storage/                          # 持久化存储
│   └── vector/chroma/                #   ChromaDB 向量数据库
│
├── ingest/pipelines/                 # 文件处理管道
├── tools/                            # 命令行工具集
│   └── core/kb/                      #   置信度评分、老化检测、Agent 文件管理
├── protocols/                        # 协议 Schema
├── tests/                            # 测试
├── benchmarks/                       # 性能基准
└── docs/                             # 文档
```

---

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动 Web 服务
cd ~/taichu && python3 clients/web/server.py 8765

# 3. 打开浏览器访问 http://localhost:8765
```

详细使用方法见 [`KB_ACCESS_PROTOCOL.md`](KB_ACCESS_PROTOCOL.md)。

---

## 核心能力

### 可视化 — 星云

| 引擎 | 描述 |
|------|------|
| **Canvas 2D** | 螺旋星系布局，悬停高亮，缩放/平移 |
| **Three.js 3D** | 全息模式，轨道漫游，粒子效果 |
| **设置面板** | 6 项画质控制（渲染引擎/视图模式/布局/节点数/转速/大小） |

### API 服务（:8765）

| 分类 | 端点 |
|------|------|
| **搜索** | `GET /api/kb/search` · `GET /api/kb/ask` · `GET /api/kb/graph` |
| **记忆** | `POST /api/kb/memory` · `GET /api/kb/memory` · `POST /api/kb/memory/summarize` |
| **Agent** | `POST /api/agents/register` · `POST /api/agents/heartbeat` · `GET /api/agents` |
| **Agent 文件** | `GET/PUT /api/agents/{id}/profile` · `GET/PUT /api/agents/{id}/personality` · `GET /api/agents/{id}/sessions` |
| **老化检测** | `GET /api/kb/aging/report` · `GET /api/kb/aging/review` · `GET /api/kb/aging/archive-suggestions` |
| **写入** | `POST /upload` · `POST /api/kb/compile` |
| **系统** | `GET /health` · `GET /api/stats` · `GET /api/metrics` · `WS /ws` |

完整 API 参考见 [`KB_ACCESS_PROTOCOL.md`](KB_ACCESS_PROTOCOL.md) 和 [`docs/REFERENCE.md`](docs/REFERENCE.md)。

### 模型管理

- 8+ 内置 Provider：Ollama、火山引擎、阿里云、百度千帆、智谱、DeepSeek、Moonshot、SiliconFlow、OpenRouter、302.AI
- 5 个角色：compile（编译）、query（查询）、reasoning（推理）、embedding（嵌入）、vision（视觉）
- Web UI 可视化切换，自动回写 `config/models.yaml`

### Runtime 引擎

| 模块 | 说明 |
|------|------|
| **6 阶段检索** | 查询解析 → 向量搜索 → 图谱扩展 → 本体过滤 → 重排序 → 上下文构建 |
| **GBrain 语义智能** | 关系推断、聚类检测、语义重力、本体构建 |
| **GEP 自演化** | 基因组 → 变异 → 沙盒实验 → 适应度评估闭环 |
| **多 Agent 系统** | RetrievalAgent、GraphAgent、MemoryAgent、SynthesizerAgent、PlannerAgent |
| **Semantic Attention** | 全局注意力场、路由、传播、热点聚类、涌现生态 |
| **事件总线** | 10 种内部事件 → WebSocket 广播 |
| **知识老化检测** | 三因子评分（时间/频率/置信度），四级分类 |
| **跨会话记忆** | Agent 记忆持久化到 ChromaDB，重启不丢失 |

### 知识摄取

- 20+ 文件格式支持（md/pdf/docx/pptx/html/txt/csv/xlsx/epub/图片/代码）
- 自动去重、格式转换、wiki 编译
- 归档层完整追溯（raw/manifest/provenance/fingerprint）
- 双索引：ChromaDB 向量索引 + GraphBuilder 图谱索引

---

## 客户端对比

| 特性 | Web UI | Tauri 桌面端 |
|------|:------:|:------------:|
| 渲染引擎 | Canvas 2D / Three.js 3D | Canvas 2D / Three.js 3D |
| 上传方式 | 浏览器拖拽 | 系统原生拖拽 |
| WS 推送 | 支持 | 已启用 |
| 模型切换 | 设置页 | 设置页 |
| 语言切换 | 设置页 | 设置页 |

---

## 文档索引

| 文档 | 用途 |
|------|------|
| `KB_ACCESS_PROTOCOL.md` | Agent 使用协议（外部 Agent/工具 必读）|
| `docs/REFERENCE.md` | 完整参考手册（架构/API/配置/开发） |
| `config/paths.yaml` | 统一路径配置 |
| `config/models.yaml` | 模型/Provider 配置 |

---

## 版本

v3.4.0 — 2026-05-16

- Agent 专属文件系统（profile/personality/sessions）
- 知识老化检测系统（三因子评分，四级分类）
- 跨会话记忆持久化（ChromaDB）
- 中英双语界面
- Tauri 桌面端原生拖拽上传
- 自研星云渲染引擎（Canvas 2D + Three.js 3D）
