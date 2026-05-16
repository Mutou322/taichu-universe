# 太初知识宇宙 — 完整参考手册

> 项目全局参考文档，涵盖架构、API、配置、开发等全部细节。
> 新读者请从 [README.md](../README.md) 或 [KB_ACCESS_PROTOCOL.md](../KB_ACCESS_PROTOCOL.md) 开始。

---

## 目录

- [1. 项目概览](#1-项目概览)
- [2. 架构详解](#2-架构详解)
- [3. 完整 API 参考](#3-完整-api-参考)
- [4. 配置中心](#4-配置中心)
- [5. 数据模型](#5-数据模型)
- [6. 开发指南](#6-开发指南)

---

## 1. 项目概览

太初知识宇宙（Taichu Knowledge Universe）是一个自演化 AI 知识图谱平台，核心能力：

- **知识管理**：Markdown 词条 + ChromaDB 向量索引 + 知识图谱
- **多 Agent 系统**：5 种内置 Agent 类型，支持外部 Agent 接入
- **AI Runtime**：6 阶段检索管道、GBrain 语义智能、GEP 自演化
- **老化检测**：三因子评分自动标记知识时效性
- **跨会话记忆**：Agent 记忆持久化，重启不丢失
- **双客户端**：Web UI（浏览器）+ Tauri 桌面端

| 项目 | 值 |
|------|-----|
| API 端口 | `http://127.0.0.1:8765` |
| 内容规模 | ~1400 wiki 词条 + 200+ 归档 |
| 图谱规模 | ~630 节点 / ~290 边 |
| 存储引擎 | ChromaDB + Markdown 文件 |
| 桌面客户端 | Tauri（1200x800，原生拖拽上传） |
| 许可证 | MIT |

---

## 2. 架构详解

### 2.1 目录结构

```
taichu/
├── runtime/                          # AI Runtime 引擎层
│   ├── agents/                       #   多 Agent 系统
│   ├── memory/                       #   内存管理（ChromaDB + 跨会话记忆）
│   ├── semantic/                     #   语义引擎
│   ├── retrieval/                    #   6 阶段检索管道
│   ├── gbrain/                       #   语义智能中枢
│   ├── attention/                    #   注意力机制（14 模块）
│   ├── evolution/                    #   GEP 自演化
│   ├── planning/                     #   DAG 工作流
│   ├── scheduler/                    #   自适应调度器
│   ├── capabilities/                 #   能力路由
│   ├── specialization/               #   Agent 特化
│   ├── events/                       #   事件总线 + WebSocket
│   ├── metrics/                      #   可观测性
│   ├── ingestion/                    #   知识摄取
│   ├── archive/                      #   文件存档
│   ├── bootstrap.py                  #   统一入口
│   ├── phase9_main.py                #   主循环
│   └── phase9_archive_runtime.py     #   存档运行时
│
├── clients/                          # 客户端
│   ├── web/                          #   Web UI（FastAPI :8765）
│   │   ├── server.py                 #   主服务 + REST API
│   │   └── static/
│   │       ├── kb.js                 #   前端核心逻辑
│   │       └── style.css             #   深色主题
│   └── tauri/                        #   Tauri 桌面端
│       └── tauri-ui/
│           ├── frontend/             #   HTML/JS/CSS
│           └── src-tauri/src/        #   Rust 后端
│
├── knowledge/                        # 知识库内容
│   ├── wiki/                         #   Markdown 词条
│   ├── wiki/_archived/               #   归档（只读）
│   ├── agents/                       #   Agent 专属文件
│   ├── graph/                        #   图谱构建器
│   ├── relations/                    #   关系定义
│   └── references/                   #   参考代码
│
├── config/                           # 统一配置
│   ├── paths.yaml                    #   路径配置
│   ├── models.yaml                   #   模型/Provider
│   ├── paths.py                      #   路径读取器
│   └── models.py                     #   模型读取器
│
├── storage/                          # 持久化存储
│   ├── vector/chroma/                #   ChromaDB
│   ├── embeddings/                   #   嵌入器
│   ├── snapshots/                    #   快照
│   └── raw/                          #   原始上传
│
├── ingest/pipelines/                 # 文件处理管道
├── tools/                            # 命令行工具
│   ├── doubao_manager.py             #   LLM 管理/搜索/编译
│   ├── build_chromadb_index.py       #   构建/验证索引
│   ├── compile_openviking_archive.py #   归档编译器
│   ├── scripts/                      #   Wiki frontmatter 迁移等
│   └── core/kb/                      #   置信度/老化/Agent 文件管理
│
├── protocols/                        # 协议 Schema
│   ├── agent/messages.py             #   Agent 消息格式
│   ├── graph/schema.py               #   图谱 Schema
│   ├── memory/schema.py              #   记忆 Schema
│   └── websocket/events.py           #   WebSocket 事件
│
├── tests/                            # 测试
├── docs/                             # 文档
│   └── ARCHITECTURE.md               #   架构设计
├── benchmarks/                       # 性能基准
└── _deprecated/                      # 废弃代码
```

### 2.2 检索管道

6 阶段语义检索链路：

```
query_parser → vector_search → graph_expand → ontology_filter → rerank → context_builder
```

- 降级链：豆包 API → ChromaDB 本地向量搜索 → 关键词 BM25
- 全链路追踪：`GET /api/pipeline/trace?q=xxx`

### 2.3 Agent 系统

| Agent 类型 | 职责 |
|------------|------|
| RetrievalAgent | 信息检索与查询 |
| GraphAgent | 图谱分析与关系发现 |
| MemoryAgent | 语义记忆存取 |
| SynthesizerAgent | 综合分析与生成 |
| PlannerAgent | 任务分解与规划 |

路由规则：Capability Matcher 根据 task_type 匹配对应 Agent。
注意力机制：Semantic Attention Runtime 确保高 affinity 的 Agent 优先处理节点。

### 2.4 自演化系统

```
Metrics → GBrain → GEP → Agent
```

- GBrain：关系推断、聚类检测、语义重力、本体构建
- GEP：基因组 → 变异 → 沙盒实验 → 适应度评估闭环

### 2.5 事件系统

WebSocket 推送 `ws://127.0.0.1:8765/ws`：

| 事件 | 触发时机 |
|------|----------|
| `memory:stored` | 记忆存储完成 |
| `memory:deleted` | 记忆删除完成 |
| `graph:updated` | 图谱更新 |
| `retrieval:vector_results` | 向量搜索结果 |
| `retrieval:pipeline_completed` | 检索管道完成 |
| `semantic_gravity` | 语义重力计算完成 |
| `graph_clusters` | 聚类检测完成 |
| `ontology_metrics` | 本体构建指标 |
| `gep_sandbox_fitness` | GEP 沙盒适应度 |
| `gep_multi_agent_fitness` | 多 Agent 适应度 |

---

## 3. 完整 API 参考

### 3.1 系统

#### 健康检查

```bash
curl http://127.0.0.1:8765/health
# → {"status":"ok"}
```

#### 知识库统计

```bash
curl http://127.0.0.1:8765/api/stats
# → {"wiki_count": ..., "archived_count": ..., "chroma_count": ...}
```

#### 运行时指标

```bash
curl http://127.0.0.1:8765/api/metrics
# → {"retrieval": ..., "graph": ..., "memory": ..., "eventbus": ...}
```

### 3.2 Agent 生命周期

#### 注册

```bash
curl -X POST http://127.0.0.1:8765/api/agents/register \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "my-agent", "type": "external", "meta": {"version": "1.0"}}'
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `agent_id` | string | **必填**。唯一标识 |
| `type` | string | `external`（默认）、`retrieval`、`memory` 等 |
| `meta` | dict | 附加信息（版本、能力描述等） |

注册自动创建 `knowledge/agents/{agent_id}/` 目录，含 `profile.yaml`、`personality.md`、`sessions/`。

#### 心跳

建议每 30-60 秒调用一次。超过 60 秒无心跳视为离线。

```bash
curl -X POST http://127.0.0.1:8765/api/agents/heartbeat \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "my-agent"}'
```

#### 获取 Agent 列表

```bash
curl http://127.0.0.1:8765/api/agents
# → {"agents": [{"agent_id": "my-agent", "type": "external", "online": true, "last_seen": ...}], "total": 1}
```

在线判定：心跳时间不超过 60 秒。

### 3.3 Agent 文件管理

每个 Agent 拥有专属目录：

```
knowledge/agents/{agent_id}/
├── profile.yaml         # 系统自维护（type、meta、last_seen）
├── personality.md       # 人格设定（可编辑）
└── sessions/
    └── YYYY-MM-DD.md   # 按天切分的会话日志
```

#### 读取/更新 Profile

```bash
curl http://127.0.0.1:8765/api/agents/my-agent/profile
# → {"agent_id": "my-agent", "profile": {"type": "external", "last_seen": ...}}

curl -X PUT http://127.0.0.1:8765/api/agents/my-agent/profile \
  -H "Content-Type: application/json" \
  -d '{"meta": {"version": "2.0"}}'
```

`profile.yaml` 字段：
| 字段 | 说明 |
|------|------|
| `agent_id` | Agent 标识 |
| `type` | Agent 类型 |
| `meta` | 自定义元数据 |
| `created_at` | 创建时间（ISO 8601） |
| `last_seen` | 最后活跃时间（自动更新） |

#### 读取/更新 Personality

```bash
curl http://127.0.0.1:8765/api/agents/my-agent/personality
# → {"agent_id": "my-agent", "personality": "# my-agent\n\nPersonality and instructions..."}

curl -X PUT http://127.0.0.1:8765/api/agents/my-agent/personality \
  -H "Content-Type: application/json" \
  -d '{"content": "# My Agent\n\nCustom personality."}'
```

#### 会话日志

```bash
# 列出所有会话日期
curl http://127.0.0.1:8765/api/agents/my-agent/sessions
# → {"agent_id": "my-agent", "sessions": [{"date": "2026-05-16", "entries": 12}], "total": 1}

# 获取某日完整日志
curl http://127.0.0.1:8765/api/agents/my-agent/sessions/2026-05-16
# → {"agent_id": "my-agent", "date": "2026-05-16", "content": "- **12:07:57** | message: ..."}
```

会话日志在保存记忆时自动追加，按 `YYYY-MM-DD.md` 切分。

### 3.4 知识检索

#### 语义搜索

```bash
curl -G 'http://127.0.0.1:8765/api/kb/search' \
  --data-urlencode 'q=查询关键词' \
  --data-urlencode 'min_confidence=0.3' \
  --data-urlencode 'limit=10'
```

| 参数 | 默认 | 说明 |
|------|------|------|
| `q` | — | **必填**。搜索关键词 |
| `min_confidence` | 0 | 最低置信度过滤（0.0–1.0） |
| `limit` | 10 | 最大结果数 |
| `group` | false | 按类型分组输出 |

返回降级链：豆包 API → ChromaDB → 关键词 BM25。

#### RAG 问答

```bash
curl -G 'http://127.0.0.1:8765/api/kb/ask' \
  --data-urlencode 'q=你的问题'
```

使用 compile 角色模型进行检索增强生成。

#### 知识图谱

```bash
#  Top 150 节点
curl 'http://127.0.0.1:8765/api/kb/graph'

#  全量节点
curl 'http://127.0.0.1:8765/api/kb/graph?limit=0'

#  指定节点子图
curl 'http://127.0.0.1:8765/api/kb/graph?expand=NODE_ID'
```

#### 检索管道追踪

```bash
curl 'http://127.0.0.1:8765/api/pipeline/trace?q=查询'
```

返回 6 阶段耗时明细。

### 3.5 跨会话记忆

#### 保存记忆

```bash
curl -X POST http://127.0.0.1:8765/api/kb/memory \
  -H "Content-Type: application/json" \
  -d '{"content": "用户偏好使用深色主题", "agent_id": "hermes", "type": "user_preference", "importance": 0.8, "session_id": "my-session-001"}'
```

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `content` | string | — | **必填**。记忆内容 |
| `agent_id` | string | taichu | Agent 标识 |
| `session_id` | string | 自动生成 | 会话 ID |
| `type` | string | conversation | conversation / decision / insight / summary / user_preference |
| `importance` | float | 0.6 | 重要性（低 0.3 / 正常 0.6 / 高 0.9） |
| `summary` | string | content 前 60 字 | 简短摘要 |

保存后自动追加到 Agent 当日会话日志。

#### 检索记忆

```bash
curl "http://127.0.0.1:8765/api/kb/memory?q=关键词&agent=hermes&limit=5&types=insight,decision"
```

| 参数 | 默认 | 说明 |
|------|------|------|
| `q` | — | **必填**。搜索关键词 |
| `agent` | 空 | 限定 Agent（空=搜索所有） |
| `limit` | 10 | 最大结果数 |
| `types` | 空 | 限定类型（逗号分隔） |

#### 列出会话

```bash
curl "http://127.0.0.1:8765/api/kb/memory/sessions?agent=hermes&limit=50"
```

#### 压缩会话

```bash
curl -X POST http://127.0.0.1:8765/api/kb/memory/summarize \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "hermes", "session_id": "my-session-001"}'
```

### 3.6 知识写入

#### 上传文件

```bash
curl -X POST -F 'files=@myfile.md' http://127.0.0.1:8765/upload
# 多文件：-F 'files=@a.md' -F 'files=@b.pdf'
```

支持格式：
- 文档：`.md` `.pdf` `.docx` `.pptx` `.html` `.htm` `.txt` `.csv` `.xlsx` `.epub`
- 图片：`.png` `.jpg` `.jpeg` `.webp` `.gif` `.bmp`
- 代码：`.py` `.js` `.ts` `.yaml` `.toml`

上传后 `.md` 直接进入 `knowledge/wiki/`，其余进入 `ingest/inbox/` 待编译。

#### 编译待处理文件

```bash
curl -X POST http://127.0.0.1:8765/api/kb/compile
```

### 3.7 置信度评分

```bash
# 查询单文件
curl 'http://127.0.0.1:8765/api/kb/confidence?file=knowledge/wiki/my-article.md'

# 查询所有
curl 'http://127.0.0.1:8765/api/kb/confidence'
```

评分因子（5 因子，0.0–1.0）：
| 因子 | 权重 | 说明 |
|------|:----:|------|
| Source field | 见配置 | frontmatter 中 source 字段存在性 |
| Source citations | 见配置 | 正文中 `^source::` 引用数量 |
| Content structure | 见配置 | `##` 标题层级丰富度 |
| Wiki-links | 见配置 | `[[` 内部链接密度 |
| Content length | 见配置 | 字符数 |

### 3.8 老化检测

三因子评分（0.0–1.0，越高越老）：

| 因子 | 权重 | 说明 |
|:----|:----:|------|
| T（时间衰减） | 0.4 | 最后访问时间距今天数 / 90 天阈值 |
| F（频率因子） | 0.3 | 访问次数相对同层文章 |
| C（置信度因子） | 0.3 | 1 - confidence_score |

四级分类：

| 层级 | 分数 | 行为 |
|:-----|:----:|:-----|
| 🟢 Active | < 0.3 | 无操作 |
| 🟡 Notice | 0.3–0.5 | frontmatter 标记 `aging: true` |
| 🟠 Aging | 0.5–0.7 | 标记 + 写入事件日志 |
| 🔴 Stale | > 0.7 | 标记 + 建议归档 |

老化检测只做标记和建议，不删不改文件，搜索不受影响。

```bash
# 老化统计摘要
curl http://127.0.0.1:8765/api/kb/aging/report

# 需重审文章（notice + aging 级）
curl http://127.0.0.1:8765/api/kb/aging/review

# 建议归档文章（stale 级）
curl http://127.0.0.1:8765/api/kb/aging/archive-suggestions

# 老化事件日志
curl http://127.0.0.1:8765/api/kb/aging/events

# 排行榜（支持 min_score / limit / tier 过滤）
curl 'http://127.0.0.1:8765/api/kb/aging?limit=20&tier=stale'

# 批量写入 frontmatter aging:true
curl -X POST http://127.0.0.1:8765/api/kb/aging/apply
```

### 3.9 模型管理

```bash
# 获取模型配置/Provider 列表
curl http://127.0.0.1:8765/api/models

# 切换模型 Provider
curl -X POST http://127.0.0.1:8765/api/models/switch \
  -H "Content-Type: application/json" \
  -d '{"role": "compile", "provider": "deepseek"}'
```

#### 内置 Provider

Ollama、火山引擎 Doubao、阿里云 DashScope、百度千帆、智谱 GLM、DeepSeek、Moonshot（Kimi）、SiliconFlow、OpenRouter、302.AI

#### 模型角色

| 角色 | 用途 | 默认 Provider |
|------|------|---------------|
| `compile` | 文档编译、RAG 问答、知识推理 | volcengine |
| `query` | 快速问答 | ollama |
| `reasoning` | 复杂推理 | ollama |
| `embedding` | 向量搜索、语义索引 | volcengine |
| `vision` | 图片分析、OCR | volcengine |

Web UI 设置页可视化切换，自动回写 `config/models.yaml`。

---

## 4. 配置中心

### 4.1 路径配置 `config/paths.yaml`

```yaml
root: ~/taichu

knowledge:
  wiki: ~/taichu/knowledge/wiki
  graph: ~/taichu/knowledge/graph
  ontology: ~/taichu/knowledge/ontology
  clusters: ~/taichu/knowledge/clusters
  timelines: ~/taichu/knowledge/timelines
  relations: ~/taichu/knowledge/relations
  agents: ~/taichu/knowledge/agents

storage:
  vector: ~/taichu/storage/vector
  chroma: ~/taichu/storage/vector/chroma
  embeddings: ~/taichu/storage/embeddings
  cache: ~/taichu/storage/cache
  snapshots: ~/taichu/storage/snapshots
  indexes: ~/taichu/storage/indexes
  raw: ~/taichu/storage/raw
```

所有模块通过 `from config.paths import paths` 读取，禁止硬编码。

### 4.2 模型配置 `config/models.yaml`

模型角色、Provider 端点、API 密钥在此文件中管理。通过 Web UI 设置页可视化编辑。

### 4.3 老化检测阈值

在 `tools/core/kb/aging.py` 中配置：

| 参数 | 默认值 | 说明 |
|------|:------:|------|
| `THRESHOLD_DAYS` | 90 | 完全老化天数阈值 |
| `ACCESS_DECAY_DAYS` | 30 | 访问次数半衰期 |
| `TIER_ACTIVE` | 0.3 | Active / Notice 分界 |
| `TIER_NOTICE` | 0.5 | Notice / Aging 分界 |
| `TIER_AGING` | 0.7 | Aging / Stale 分界 |

---

## 5. 数据模型

### 5.1 Wiki Frontmatter

```yaml
---
type: article          # article / session / note
title: 文章标题
tags: ['article']
date: 2026-05-16
created_at: 2026-05-16T12:00:00Z   # 自动注入
aging: true                          # 老化检测标记（自动）
---
```

文章类型：
| 类型 | 识别前缀 |
|------|----------|
| `article` | `study-`, `archive-`, `design-`, `karpathy-`, `architecture-`, `reference-`, `project-`, `operation-`, `minicpm-`, `holographic-`, `nebula-`, `TEMPLATE-` |
| `session` | `session-`, `会话-` |
| `note` | `obsidian-`, `nv-`, `test-`, `web-`, `tauri-`, `system-`, `roadmap-`, `report-`, `phase`, `plan-` |

### 5.2 Agent Profile

```yaml
agent_id: my-agent
type: external
meta:
  version: "1.0"
  capabilities:
    - search
    - memory
created_at: "2026-05-16T12:00:00Z"
last_seen: "2026-05-16T12:30:00Z"
```

### 5.3 会话日志格式

```
- **12:07:57** | conversation: 用户查询了 X
- **12:08:30** | decision: 决定使用方案 B
- **12:09:15** | insight: 发现模式 Y
```

### 5.4 老化事件日志

JSONL 格式，存储在 `storage/cache/aging_events.jsonl`：

```json
{"file": "knowledge/wiki/xxx.md", "score": 0.72, "tier": "stale", "timestamp": "2026-05-16T12:00:00Z", "reason": {"T": 0.8, "F": 0.6, "C": 0.7}}
```

---

## 6. 开发指南

### 6.1 环境要求

- Python 3.10+
- Node.js 18+（Tauri 前端）
- Rust 1.70+（Tauri 后端，可选）
- ChromaDB

### 6.2 安装

```bash
pip install fastapi uvicorn chromadb sentence-transformers httpx PyYAML scikit-learn

# Tauri 桌面端（可选）
cd clients/tauri/tauri-ui
cargo tauri build
```

### 6.3 启动

```bash
# Web 服务
cd ~/taichu && python3 clients/web/server.py 8765

# Phase 9 认知主循环（可选）
python3 runtime/phase9_main.py
```

### 6.4 代码规范

项目使用 pre-commit hooks，提交前自动检查：

- **black**：Python 格式化
- **isort**：导入排序
- **flake8**：代码检查
- **bandit**：安全审计（部分第三方代码跳过）
- **mypy**：类型检查（部分模块跳过）
- **trailing-whitespace / end-of-file-fixer**：基础清理

提交时对已知问题可跳过：`SKIP=bandit,mypy git commit ...`

### 6.5 架构约束

| 禁令 | 说明 |
|------|------|
| 禁止直接读 ChromaDB | 必须通过 MemoryRuntime API |
| 禁止硬编码路径 | 所有路径从 `config/paths.yaml` 读取 |
| 禁止写 `_archived/` | 归档目录只读 |
| 禁止删 `index.md` | 词条索引，所有 agent 依赖它 |
| 禁止 `sys.path.insert` 散落 | 路径管理统一走 `runtime/bootstrap.py` |
| 禁止 `references/` 纳入 git | 该目录已被 `.gitignore` 排除 |

### 6.6 测试

```bash
pytest tests/
```

### 6.7 提交规范

提交信息格式：`type: subject`，如 `feat: xxx`、`fix: xxx`、`docs: xxx`、`refactor: xxx`。

---

> 本文档自动维护。发现问题请更新此文件并提交 PR。
