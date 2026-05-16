**English** · [中文](KB_ACCESS_PROTOCOL.md)

# Taichu — Multi-Agent Access Protocol

> Any Agent / sub-agent / external tool MUST read this protocol before connecting.
> Version: v3.4.0
>
> Full Reference → [`docs/REFERENCE.md`](docs/REFERENCE.md)

---

## 1. Quick Start (5 Steps)

```bash
# 1. Health check
curl http://127.0.0.1:8765/health

# 2. Register (gets knowledge/agents/{id}/ directory)
curl -X POST http://127.0.0.1:8765/api/agents/register \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "my-agent", "type": "external"}'

# 3. Semantic search
curl -G 'http://127.0.0.1:8765/api/kb/search' --data-urlencode 'q=your query'

# 4. Save / retrieve cross-session memory
curl -X POST http://127.0.0.1:8765/api/kb/memory \
  -H "Content-Type: application/json" \
  -d '{"content": "memory content", "agent_id": "my-agent", "type": "insight", "importance": 0.8}'
curl "http://127.0.0.1:8765/api/kb/memory?q=keyword&agent=my-agent"

# 5. Heartbeat (every 30-60s, keeps online status)
curl -X POST http://127.0.0.1:8765/api/agents/heartbeat \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "my-agent"}'
```

### Hard Rules
| # | Rule |
|---|------|
| 1 | **Never read ChromaDB directly** — use REST API only |
| 2 | **Never hardcode paths** — read from `config/paths.yaml` |
| 3 | **Never write to `knowledge/wiki/_archived/`** — read-only |
| 4 | **Never delete `knowledge/wiki/index.md`** — global entry index |

---

## 2. Full API Reference

### Agent Lifecycle
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/agents/register` | POST | Register (creates `knowledge/agents/{id}/`) |
| `/api/agents/heartbeat` | POST | Heartbeat (every 30-60s) |
| `/api/agents` | GET | List all agents with online status |
| `/api/agents/{id}/profile` | GET/PUT | Read/update profile (type/meta/last_seen) |
| `/api/agents/{id}/personality` | GET/PUT | Read/update personality |
| `/api/agents/{id}/sessions` | GET | List session log dates |
| `/api/agents/{id}/sessions/{date}` | GET | Get full daily log |

### Knowledge Retrieval
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/kb/search?q=&min_confidence=` | GET | Semantic search |
| `/api/kb/ask?q=` | GET | RAG question answering |
| `/api/kb/graph?limit=&expand=` | GET | Knowledge graph data |
| `/api/pipeline/trace?q=` | GET | 6-stage pipeline trace |

### Memory Management
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/kb/memory` | POST | Save cross-session memory |
| `/api/kb/memory?q=&agent=` | GET | Semantic memory retrieval |
| `/api/kb/memory/sessions?agent=` | GET | List memory sessions |
| `/api/kb/memory/summarize` | POST | Summarize session |

### Write to Knowledge Base
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/upload` | POST | Upload file (20+ formats) |
| `/api/kb/compile` | POST | Compile pending files |

### Aging Detection (Ops)
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/kb/aging/report` | GET | Aging statistics summary |
| `/api/kb/aging/review` | GET | Articles needing review |
| `/api/kb/aging/archive-suggestions` | GET | Suggested for archive |
| `/api/kb/aging/apply` | POST | Batch write aging flags |

### System
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/api/stats` | GET | Knowledge base stats |
| `/api/metrics` | GET | Runtime metrics |
| `/api/models` | GET | Model config list |
| `/api/models/switch` | POST | Switch model Provider |
| `/ws` | WS | WebSocket event push |

---

## 3. Agent Files

Registration auto-creates `knowledge/agents/{agent_id}/`:

```
knowledge/agents/{agent_id}/
├── profile.yaml         # System-maintained (type, meta, last_seen)
├── personality.md       # Editable personality / instructions
└── sessions/
    └── YYYY-MM-DD.md   # Daily session logs (auto-appended on memory save)
```

---

## 4. Aging Detection

Articles are scored by 3 factors (time/frequency/confidence) and classified into 4 tiers. Read-only — no deletions:

| Tier | Score | Action |
|:-----|:-----:|:-------|
| 🟢 Active | < 0.3 | None |
| 🟡 Notice | 0.3–0.5 | Frontmatter flag `aging: true` |
| 🟠 Aging | 0.5–0.7 | Flag + event log entry |
| 🔴 Stale | > 0.7 | Flag + archive suggestion |

---

## 5. Appendix

### Wiki Article Format
```
---
type: article        # article / session / note
title: Article Title
tags: ['article']
date: 2026-05-16
---
```
- All wiki files must include valid frontmatter
- Filename prefix determines type (`study-`, `session-`, `obsidian-`, etc.)
- `index.md`, `README.md`, `base.md` are exempt from validation

### Model Providers
Ollama, Volcengine, Alibaba, Baidu, Zhipu, DeepSeek, Moonshot, SiliconFlow, OpenRouter, 302.AI

### Common Commands
```bash
python3 clients/web/server.py 8765     # Start server
python3 tools/doubao_manager.py compile # Compile pending files
python3 tools/doubao_manager.py index   # Rebuild vector index
python3 runtime/phase9_main.py          # Phase 9 main loop
```
