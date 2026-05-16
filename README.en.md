**English** · [中文](README.md)

# Taichu Knowledge Universe

> AI Runtime Prototype · Self-Evolving Knowledge Graph · Canvas 2D/3D Nebula Visualization
> License: MIT
>
> Full Reference → [`docs/REFERENCE.md`](docs/REFERENCE.md)

---

## Architecture

```
taichu/
├── runtime/                          # AI Runtime Engine
│   ├── agents/                       #   Multi-Agent System (5 types)
│   ├── memory/                       #   MemoryRuntime API + Session Memory
│   ├── semantic/                     #   SemanticRuntime (Graph + Semantic Engine)
│   ├── retrieval/                    #   6-Stage Retrieval Pipeline
│   ├── gbrain/                       #   Semantic Intelligence (Inference/Clustering/Gravity/Ontology)
│   ├── attention/                    #   Semantic Attention (14 modules)
│   ├── evolution/                    #   GEP Evolution (Genome/Mutation/Sandbox/Fitness)
│   ├── planning/                     #   DAG Workflow (Decomposition/Execution/Collaboration)
│   ├── scheduler/                    #   Adaptive Scheduler
│   ├── capabilities/                 #   Capability Routing
│   ├── specialization/               #   Agent Specialization Profiles
│   ├── events/                       #   Event Bus + WebSocket Bridge
│   ├── metrics/                      #   Observability (Metrics Bus/Timers/Tracing/Counters)
│   ├── ingestion/                    #   Continuous Knowledge Ingestion
│   ├── archive/                      #   File Archive Layer
│   ├── bootstrap.py                  #   Unified Runtime Entry
│   ├── phase9_main.py                #   Main Loop Entry
│   └── phase9_archive_runtime.py     #   Archive Runtime
│
├── clients/                          # Clients
│   ├── web/                          #   Web UI (FastAPI :8765)
│   │   └── static/                   #   kb.js, style.css
│   └── tauri/                        #   Tauri Desktop App
│       └── tauri-ui/
│           ├── frontend/             #   HTML + JS + CSS
│           └── src-tauri/src/        #   Rust: lib.rs, bridge.rs, kb.rs, types.rs
│
├── knowledge/                        # Knowledge Base
│   ├── wiki/                         #   Markdown Articles
│   ├── wiki/_archived/               #   Archived Articles (Read-only)
│   ├── agents/                       #   Agent Files (profile/personality/sessions)
│   ├── graph/                        #   Graph Builder
│   ├── relations/                    #   Relation Definitions
│   └── references/                   #   Reference Files (not in git)
│
├── config/                           # Configuration
├── storage/                          # Persistent Storage
│   └── vector/chroma/                #   ChromaDB Vector Database
│
├── ingest/pipelines/                 # File Processing Pipelines
├── tools/                            # CLI Tools
│   └── core/kb/                      #   Confidence, Aging, Agent File Management
├── protocols/                        # Protocol Schemas
├── tests/                            # Tests
├── benchmarks/                       # Benchmarks
└── docs/                             # Documentation
```

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the Web server
cd ~/taichu && python3 clients/web/server.py 8765

# 3. Open http://localhost:8765 in your browser
```

See [`KB_ACCESS_PROTOCOL.md`](KB_ACCESS_PROTOCOL.md) for detailed usage.

---

## Features

### Visualization — Nebula

| Engine | Description |
|--------|-------------|
| **Canvas 2D** | Spiral galaxy layout, hover highlight, zoom/pan |
| **Three.js 3D** | Holographic mode, orbital camera, particle effects |
| **Settings Panel** | 6 quality controls (engine/view/layout/nodes/speed/size) |

### API Server（:8765）

| Category | Endpoints |
|----------|-----------|
| **Search** | `GET /api/kb/search` · `GET /api/kb/ask` · `GET /api/kb/graph` |
| **Memory** | `POST /api/kb/memory` · `GET /api/kb/memory` · `POST /api/kb/memory/summarize` |
| **Agent** | `POST /api/agents/register` · `POST /api/agents/heartbeat` · `GET /api/agents` |
| **Agent Files** | `GET/PUT /api/agents/{id}/profile` · `GET/PUT /api/agents/{id}/personality` · `GET /api/agents/{id}/sessions` |
| **Aging** | `GET /api/kb/aging/report` · `GET /api/kb/aging/review` · `GET /api/kb/aging/archive-suggestions` |
| **Write** | `POST /upload` · `POST /api/kb/compile` |
| **System** | `GET /health` · `GET /api/stats` · `GET /api/metrics` · `WS /ws` |

See [`KB_ACCESS_PROTOCOL.md`](KB_ACCESS_PROTOCOL.md) and [`docs/REFERENCE.md`](docs/REFERENCE.md) for the full API reference.

### Model Management

- 8+ built-in Providers: Ollama, Volcengine, Alibaba, Baidu, Zhipu, DeepSeek, Moonshot, SiliconFlow, OpenRouter, 302.AI
- 5 roles: compile, query, reasoning, embedding, vision
- Visual switching via Web UI, auto-saves to `config/models.yaml`

### Runtime Engine

| Module | Description |
|--------|-------------|
| **6-Stage Retrieval** | Query parsing → Vector search → Graph expansion → Ontology filter → Rerank → Context building |
| **GBrain** | Relation inference, clustering, semantic gravity, ontology building |
| **GEP Evolution** | Genome → Mutation → Sandbox → Fitness evaluation loop |
| **Multi-Agent** | RetrievalAgent, GraphAgent, MemoryAgent, SynthesizerAgent, PlannerAgent |
| **Semantic Attention** | Global field, routing, propagation, hotspot clustering, emergent ecosystem |
| **Event Bus** | 10 internal events → WebSocket broadcast |
| **Aging Detection** | 3-factor scoring (time/frequency/confidence), 4-tier classification |
| **Session Memory** | Agent memory persisted in ChromaDB, survives restarts |

### Ingestion

- 20+ file formats (md/pdf/docx/pptx/html/txt/csv/xlsx/epub/images/code)
- Auto-dedup, format conversion, wiki compilation
- Full audit trail (raw/manifest/provenance/fingerprint)
- Dual index: ChromaDB vector index + GraphBuilder graph index

---

## Client Comparison

| Feature | Web UI | Tauri Desktop |
|---------|:------:|:-------------:|
| Renderer | Canvas 2D / Three.js 3D | Canvas 2D / Three.js 3D |
| Upload | Browser drag & drop | Native drag & drop |
| WS Push | Supported | Enabled |
| Model Switch | Settings page | Settings page |
| Language | Settings page | Settings page |

---

## Document Index

| Document | Purpose |
|----------|---------|
| `KB_ACCESS_PROTOCOL.md` | API protocol for external Agents/Tools |
| `docs/REFERENCE.md` | Full reference manual (architecture/API/config/dev) |
| `config/paths.yaml` | Path configuration |
| `config/models.yaml` | Model/Provider configuration |

---

## Version

v3.4.0 — 2026-05-16

- Agent file system (profile/personality/sessions)
- Knowledge aging detection (3-factor scoring, 4-tier classification)
- Cross-session memory persistence (ChromaDB)
- Bilingual UI (Chinese/English)
- Tauri native drag-and-drop upload
- Custom nebula rendering (Canvas 2D + Three.js 3D)
