[English](KB_ACCESS_PROTOCOL.en.md) · **中文**

# 太初知识宇宙 — 多 Agent 使用协议

> 任何 Agent / 子代理 / 外部工具接入前，必须阅读此协议。
> 版本: v3.4.0
>
> 📖 完整参考手册 → [`docs/REFERENCE.md`](docs/REFERENCE.md)

---

## 1. 快速入门（5 步）

```bash
# 1. 健康检查
curl http://127.0.0.1:8765/health

# 2. 注册（获得专属目录 knowledge/agents/{id}/）
curl -X POST http://127.0.0.1:8765/api/agents/register \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "my-agent", "type": "external"}'

# 3. 语义搜索
curl -G 'http://127.0.0.1:8765/api/kb/search' --data-urlencode 'q=你的查询'

# 4. 保存/检索跨会话记忆
curl -X POST http://127.0.0.1:8765/api/kb/memory \
  -H "Content-Type: application/json" \
  -d '{"content": "记忆内容", "agent_id": "my-agent", "type": "insight", "importance": 0.8}'
curl "http://127.0.0.1:8765/api/kb/memory?q=关键词&agent=my-agent"

# 5. 心跳（每 30-60s，维持在线状态）
curl -X POST http://127.0.0.1:8765/api/agents/heartbeat \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "my-agent"}'
```

### 禁令
| # | 规则 |
|---|------|
| 1 | **禁止直接读 ChromaDB**，必须通过 REST API |
| 2 | **禁止硬编码路径**，统一从 `config/paths.yaml` 读取 |
| 3 | **禁止写 `knowledge/wiki/_archived/`**，归档只读 |
| 4 | **禁止删除 `knowledge/wiki/index.md`**，词条索引全局依赖 |

---

## 2. 完整 API 参考

### Agent 生命周期
| 端点 | 方法 | 用途 |
|------|------|------|
| `/api/agents/register` | POST | 注册（自动创建 `knowledge/agents/{id}/`） |
| `/api/agents/heartbeat` | POST | 心跳（30-60s 间隔） |
| `/api/agents` | GET | 列出所有 Agent 及在线状态 |
| `/api/agents/{id}/profile` | GET/PUT | 读取/更新配置（type/meta/last_seen） |
| `/api/agents/{id}/personality` | GET/PUT | 读取/更新人格设定 |
| `/api/agents/{id}/sessions` | GET | 列出会话日志日期 |
| `/api/agents/{id}/sessions/{date}` | GET | 获取某日完整日志 |

### 知识检索
| 端点 | 方法 | 用途 |
|------|------|------|
| `/api/kb/search?q=&min_confidence=` | GET | 语义搜索 |
| `/api/kb/ask?q=` | GET | RAG 问答 |
| `/api/kb/graph?limit=&expand=` | GET | 知识图谱数据 |
| `/api/pipeline/trace?q=` | GET | 6 阶段检索链路追踪 |

### 记忆管理
| 端点 | 方法 | 用途 |
|------|------|------|
| `/api/kb/memory` | POST | 保存跨会话记忆 |
| `/api/kb/memory?q=&agent=` | GET | 语义检索记忆 |
| `/api/kb/memory/sessions?agent=` | GET | 列出记忆会话 |
| `/api/kb/memory/summarize` | POST | 压缩会话为摘要 |

### 写入知识库
| 端点 | 方法 | 用途 |
|------|------|------|
| `/upload` | POST | 上传文件（20+ 格式） |
| `/api/kb/compile` | POST | 编译待处理文件 |

### 老化检测（运维辅助）
| 端点 | 方法 | 用途 |
|------|------|------|
| `/api/kb/aging/report` | GET | 老化统计摘要 |
| `/api/kb/aging/review` | GET | 需重审的文章 |
| `/api/kb/aging/archive-suggestions` | GET | 建议归档的文章 |
| `/api/kb/aging/apply` | POST | 批量写入 aging 标记 |

### 系统
| 端点 | 方法 | 用途 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/stats` | GET | 知识库统计 |
| `/api/metrics` | GET | 运行时指标 |
| `/api/models` | GET | 模型配置列表 |
| `/api/models/switch` | POST | 切换模型 Provider |
| `/ws` | WS | WebSocket 事件推送 |

---

## 3. Agent 专属文件

注册时自动生成 `knowledge/agents/{agent_id}/`：

```
knowledge/agents/{agent_id}/
├── profile.yaml         # 系统维护（type、meta、last_seen）
├── personality.md       # 人格设定（可编辑）
└── sessions/
    └── YYYY-MM-DD.md   # 按天切分的会话日志（存记忆时自动追加）
```

---

## 4. 老化检测

文章按三因子评分（时间/频率/置信度）分四级，只标记不删改：

| 层级 | 分数 | 行为 |
|:-----|:----:|:-----|
| 🟢 Active | < 0.3 | 无操作 |
| 🟡 Notice | 0.3–0.5 | frontmatter 标记 `aging: true` |
| 🟠 Aging | 0.5–0.7 | 标记 + 事件日志 |
| 🔴 Stale | > 0.7 | 标记 + 建议归档 |

---

## 5. 附录

### Wiki 文章规范
```
---
type: article        # article / session / note
title: 文章标题
tags: ['article']
date: 2026-05-16
---
```
- Agent 写入 wiki 文件必须带 frontmatter
- 文件名前缀决定类型（`study-`、`session-`、`obsidian-` 等）
- `index.md`、`README.md`、`base.md` 跳过校验

### 模型 Provider
Ollama、火山引擎、阿里云、百度千帆、智谱、DeepSeek、Moonshot、SiliconFlow、OpenRouter、302.AI

### 常用运维命令
```bash
python3 clients/web/server.py 8765     # 启动服务
python3 tools/doubao_manager.py compile # 编译待处理文件
python3 tools/doubao_manager.py index   # 重建向量索引
python3 runtime/phase9_main.py          # Phase 9 主循环
```
