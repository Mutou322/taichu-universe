"""Taichu Knowledge Web UI (FastAPI) — 基于新 taichu 架构
提供 HTML 页面 + API 端点，适配旧版 Web UI 前端 JS 的调用格式。
"""

import json
import logging
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

TAICHU_HOME = Path(os.environ.get("TAICHU_HOME", str(Path.home() / "taichu"))).expanduser().resolve()
sys.path.insert(0, str(TAICHU_HOME))
sys.path.insert(0, str(TAICHU_HOME / "config"))

logger = logging.getLogger("taichu.web")

# 使用 taichu_venv Python 环境（含 sentence_transformers 等）
_VENV = TAICHU_HOME.parent / "taichu_venv" / "lib" / f"python3.{sys.version_info.minor}" / "site-packages"
if _VENV.exists():
    sys.path.insert(0, str(_VENV))

import uvicorn
from fastapi import FastAPI, File, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from paths import paths

try:
    from tools.core.kb.confidence import batch_confidence, compute_confidence, parse_frontmatter
except ImportError:
    logger.warning("tools.core.kb.confidence 导入失败，置信度功能不可用")
    compute_confidence = None
    batch_confidence = None
    parse_frontmatter = None

try:
    from tools.core.kb.aging import apply_aging_flag, apply_all_flags, batch_aging, get_aging_events
    from tools.core.kb.aging import report as aging_report
    from tools.core.kb.aging import suggest_archive, suggest_review
except ImportError:
    logger.warning("tools.core.kb.aging 导入失败，老化功能不可用")
    batch_aging = None
    aging_report = None
    apply_aging_flag = None
    apply_all_flags = None
    suggest_archive = None
    suggest_review = None
    get_aging_events = None

try:
    from tools.core.kb.agent_files import AgentFileManager, on_agent_registered, on_memory_stored

    _agent_file_mgr = AgentFileManager()
except ImportError:
    logger.warning("tools.core.kb.agent_files 导入失败，Agent 文件管理不可用")
    _agent_file_mgr = None
    on_memory_stored = None
    on_agent_registered = None

try:
    from runtime.memory.session_memory import get_session_memory
except ImportError:
    logger.warning("runtime.memory.session_memory 导入失败，会话记忆不可用")
    get_session_memory = None

from runtime.events.bus import bus
from runtime.events.ws_bridge import register_ws_handlers

# ── 静态文件 ──
STATIC_DIR = Path(__file__).parent / "static"

# ── 运行时（惰性初始化）──
from runtime.bootstrap import get_memory, get_semantic

memory = None
semantic = None
_kb_models_module = None


def ensure_memory() -> bool:
    """确保 memory 已初始化，返回 bool"""
    global memory
    if memory is None:
        memory = get_memory()
    return memory is not None


def ensure_semantic() -> bool:
    """确保 semantic 已初始化，返回 bool"""
    global semantic
    if semantic is None:
        semantic = get_semantic()
    return semantic is not None


def _load_kb_models():
    """单次加载 kb_models 模块，复用全局缓存，避免每次搜索都 exec_module"""
    global _kb_models_module
    if _kb_models_module is not None:
        return _kb_models_module
    from pathlib import Path

    km = str(paths.kb_models)
    km_dir = str(Path(km).parent)
    old_sys_path = sys.path.copy()
    try:
        sys.path.insert(0, km_dir)
        import importlib.util

        spec = importlib.util.spec_from_file_location("kb_models", km)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _kb_models_module = mod
        return mod
    except Exception as e:
        logger.warning(f"kb_models 加载失败: {e}")
        _kb_models_module = None
        return None
    finally:
        sys.path[:] = old_sys_path


# 从 pipelines 导入支持的文件类型，保持同步
from ingest.pipelines import UPLOAD_EXTENSIONS as SUPPORTED_EXT_KEYS

SUPPORTED_EXT = set(SUPPORTED_EXT_KEYS)


PAGE_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>知识宇宙 — Taichu Universe</title>
<script src="https://cdn.jsdelivr.net/npm/vis-network@9.1.6/dist/vis-network.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<link rel="stylesheet" href="/static/style.css">
<style>
.confidence-badge{display:inline-block;padding:2px 10px;border-radius:10px;font-size:11px;font-weight:600;color:#050816;margin-right:8px;min-width:36px;text-align:center;}
.search-results-container{display:flex;flex-direction:column;gap:6px;margin-bottom:12px;}
.search-result-item{display:flex;align-items:center;gap:8px;padding:8px 12px;background:rgba(255,255,255,0.03);border-radius:6px;font-size:13px;border:1px solid rgba(255,255,255,0.04);}
.search-result-item .result-title{flex:1;color:rgba(255,255,255,0.85);}
.search-result-item .result-score{font-size:11px;color:rgba(255,255,255,0.35);}
.search-filter-row{display:flex;align-items:center;gap:8px;margin:10px 0;padding:8px 0;}
.search-filter-row select{padding:4px 8px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:4px;color:#fff;font-size:12px;outline:none;cursor:pointer;}
.search-filter-row select option{background:#1a1a2e;color:#fff;}
.filter-label{font-size:12px;color:rgba(255,255,255,0.6);}
.conf-badge{display:inline-block;padding:1px 6px;border-radius:8px;font-size:10px;font-weight:600;color:#050816;text-align:center;min-width:28px;}
.search-group{margin-bottom:14px;}
.search-group-title{font-size:13px;font-weight:600;color:#d4af37;margin-bottom:6px;padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.06);}
.type-checkbox{display:inline-flex;align-items:center;gap:4px;margin-right:12px;font-size:12px;color:rgba(255,255,255,0.7);cursor:pointer;}
.type-checkbox input{cursor:pointer;}
.group-mode-btn{padding:3px 10px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:4px;color:rgba(255,255,255,0.6);font-size:12px;cursor:pointer;margin-right:6px;}
.group-mode-btn.active{background:rgba(212,175,55,0.15);border-color:#d4af37;color:#d4af37;}
.result-summary{font-size:11px;color:rgba(255,255,255,0.4);line-height:1.4;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;margin-top:2px;}
</style>
</head>
<body>

<div id="navbar">
  <div class="nav-item active" data-tab="home" data-i18n="nav.home">🌌 知识宇宙</div>
  <div class="nav-item" data-tab="upload" data-i18n="nav.upload">📤 上传</div>
  <div class="nav-item" data-tab="entries" data-i18n="nav.entries">📄 词条</div>
  <div class="nav-item" data-tab="semantic" data-i18n="nav.semantic">🔍 语义搜索</div>
  <div class="nav-item" data-tab="memory" data-i18n="nav.memory">🧠 Agent 记忆</div>
  <div class="nav-item" data-tab="aging" data-i18n="nav.aging">📊 老化列表</div>
  <div class="nav-item" data-tab="settings" data-i18n="nav.settings">⚙ 设置</div>
</div>

<div id="content-area">

  <!-- 🌌 HOME: stats + nebula -->
  <div id="tab-home">
        <div class="nebula-section">
      <div class="nebula-header" data-i18n="nebula.title">🌌 知识星云</div>
      <div class="nebula-search-row">
        <input id="nebula-search-input" type="text" placeholder="输入节点名称跳转..." data-i18n-placeholder="nebula.search_placeholder" onkeydown="if(event.key==='Enter')doNebulaSearch()">
        <button onclick="doNebulaSearch()" data-i18n="nebula.goto">跳转</button>
      </div>
      <div class="nebula-graph-wrap">
        <div id="kb-graph"></div>
        <div id="panel" style="position:absolute;top:10px;right:10px;width:320px;max-height:90vh;background:rgba(0,0,0,0.85);color:#fff;padding:10px;overflow-y:auto;border-radius:6px;z-index:1000;border:1px solid rgba(255,255,255,0.08);">
          <h2 id="panel-title" style="margin:0 0 6px 0;font-size:14px;color:#7dd3fc;line-height:1.4;">知识节点</h2>
          <div id="panel-content" style="font-size:11px;line-height:1.6;min-height:50px;" data-i18n="panel.placeholder">悬停节点查看详情</div>
        </div>
      </div>
      <div class="nebula-hint" data-i18n="nebula.hint">滚轮缩放 · 双击聚焦</div>
    </div>
  </div>

  <!-- 📤 UPLOAD -->
  <div id="tab-upload">
    <div class="upload-section">
      <div style="font-size:15px;font-weight:600;margin-bottom:12px;" data-i18n="upload.title">📤 上传文件</div>
      <div class="stats-row" id="stats-bar"></div>
      <div class="upload-zone" id="dropzone-upload">
        <div class="icon">✦</div>
        <div class="text" data-i18n="upload.drop">拖放文件到此处，或点击选择</div>
        <div class="hint" data-i18n="upload.hint">.md → 直接发布 · 其他格式 → raw/ + 编译</div>
        <input type="file" id="file-input-upload" accept=".md,.pdf,.docx,.pptx,.html,.htm,.txt,.csv,.xlsx,.epub,.png,.jpg,.jpeg,.webp,.gif,.bmp,.py,.js,.ts,.yaml,.toml" multiple>
      </div>
      <div id="result-upload"></div>
      <ul id="file-list" style="list-style:none;padding:6px 0;margin:0 0 10px 0;color:rgba(255,255,255,0.8);font-size:13px;"></ul>
      <div class="pending-section">
        <div class="pending-header">
          <h3 data-i18n="upload.pending">📋 待编译文件 <span id="pending-badge-upload"></span></h3>
          <button class="compile-btn" onclick="triggerCompile()" data-i18n="upload.compile_all">⚡ 编译全部</button>
          <button onclick="refreshPending()" style="padding:7px 12px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:5px;color:rgba(255,255,255,0.6);font-size:12px;cursor:pointer;">⟳</button>
        </div>
        <div id="pending-list-upload">
          <div class="empty" data-i18n="upload.empty">✦ 没有待处理文件</div>
        </div>
      </div>
    </div>
  </div>

  <!-- 📄 ENTRIES -->
  <div id="tab-entries">
    <h3 data-i18n="entries.title">📄 词条</h3>
    <div class="subtitle" data-i18n="entries.subtitle">全部词条列表</div>
    <div id="wiki-panel"></div>
  </div>

  <!-- 🔍 SEMANTIC SEARCH -->
  <div id="tab-semantic">
    <div class="search-section">
      <div class="search-header" data-i18n="search.title">🔍 语义搜索</div>
      <div class="search-body">
        <div class="search-bar">
          <input id="search-input" type="text" placeholder="输入搜索词或问题..." data-i18n-placeholder="search.placeholder" onkeydown="if(event.key==='Enter')doSearch()">
          <button onclick="doSearch()" data-i18n="search.btn">搜索</button>
        </div>
        <div class="search-modes">
          <button id="mode-search" onclick="setSearchMode('search')" class="active" data-i18n="search.semantic">🔎 语义检索</button>
          <button id="mode-ask" onclick="setSearchMode('ask')" data-i18n="search.ask">💬 AI 问答</button>
        </div>
        <div class="search-filter-row">
          <label class="filter-label" data-i18n="search.min_confidence">最低置信度</label>
          <select id="confidence-filter">
            <option value="0" data-i18n="search.confidence_any">全部</option>
            <option value="0.3">&gt;= 0.3</option>
            <option value="0.5" selected>&gt;= 0.5</option>
            <option value="0.7">&gt;= 0.7</option>
          </select>
        </div>
        <div class="search-filter-row" id="type-filter-row">
          <label class="filter-label" data-i18n="search.filter_type">类型过滤</label>
          <label class="type-checkbox"><input type="checkbox" value="article" checked> <span data-i18n="search.type_article">文章</span></label>
          <label class="type-checkbox"><input type="checkbox" value="session" checked> <span data-i18n="search.type_session">会话</span></label>
          <label class="type-checkbox"><input type="checkbox" value="note" checked> <span data-i18n="search.type_note">笔记</span></label>
        </div>
        <div class="search-filter-row" id="group-mode-row">
          <label class="filter-label">分组</label>
          <button class="group-mode-btn active" data-group="type" data-i18n="search.group_type">按类型</button>
          <button class="group-mode-btn" data-group="confidence" data-i18n="search.group_confidence">按置信度</button>
        </div>
        <div id="search-result">
          <div class="placeholder" data-i18n="search.no_query">输入关键词进行语义搜索，或切换至"AI 问答"模式获取回答。</div>
        </div>
      </div>
    </div>
  </div>


  <!-- 🧠 AGENT 记忆 -->
  <div id="tab-memory" style="padding:20px;">
    <div style="font-size:18px;font-weight:600;margin-bottom:16px;" data-i18n="memory.title">🧠 Agent 记忆管理</div>
    <div style="display:flex;gap:14px;flex-wrap:wrap;margin-bottom:20px;">
      <div id="mem-agent-count" class="stat-card" style="background:rgba(255,255,255,0.03);border-radius:10px;padding:20px;border:1px solid rgba(255,255,255,0.06);min-width:140px;flex:1;">
        <div style="font-size:28px;font-weight:700;color:#7dd3fc;">-</div>
        <div style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:4px;">接入 Agent</div>
      </div>
      <div id="mem-total-count" class="stat-card" style="background:rgba(255,255,255,0.03);border-radius:10px;padding:20px;border:1px solid rgba(255,255,255,0.06);min-width:140px;flex:1;">
        <div style="font-size:28px;font-weight:700;color:#fbbf24;">-</div>
        <div style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:4px;">记忆总条数</div>
      </div>
      <div id="mem-session-count" class="stat-card" style="background:rgba(255,255,255,0.03);border-radius:10px;padding:20px;border:1px solid rgba(255,255,255,0.06);min-width:140px;flex:1;">
        <div style="font-size:28px;font-weight:700;color:#a78bfa;">-</div>
        <div style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:4px;">会话数</div>
      </div>
    </div>
    <div style="display:flex;gap:10px;margin-bottom:20px;">
      <div style="flex:1;background:rgba(255,255,255,0.03);border-radius:10px;padding:8px;border:1px solid rgba(255,255,255,0.06);">
        <div style="font-size:12px;font-weight:600;margin-bottom:4px;color:rgba(255,255,255,0.8);text-align:center;" data-i18n="memory.agent_dist">Agent 分布</div>
        <canvas id="memory-agent-chart" width="80" height="80" style="display:block;margin:0 auto;"></canvas>
      </div>
      <div style="flex:1;background:rgba(255,255,255,0.03);border-radius:10px;padding:8px;border:1px solid rgba(255,255,255,0.06);">
        <div style="font-size:12px;font-weight:600;margin-bottom:4px;color:rgba(255,255,255,0.8);text-align:center;" data-i18n="memory.type_dist">记忆类型分布</div>
        <canvas id="memory-type-chart" width="80" height="80" style="display:block;margin:0 auto;"></canvas>
      </div>
    </div>
    <div style="background:rgba(255,255,255,0.03);border-radius:10px;padding:20px;border:1px solid rgba(255,255,255,0.06);margin-bottom:20px;">
      <div style="font-size:14px;font-weight:600;margin-bottom:12px;color:rgba(255,255,255,0.8);" data-i18n="memory.recent">最近会话</div>
      <div id="memory-recent-list" style="font-size:13px;color:rgba(255,255,255,0.6);" data-i18n="memory.loading">加载中...</div>
    </div>
    <div style="background:rgba(255,255,255,0.03);border-radius:10px;padding:20px;border:1px solid rgba(255,255,255,0.06);">
      <div style="font-size:14px;font-weight:600;margin-bottom:12px;color:rgba(255,255,255,0.8);" data-i18n="memory.detail">Agent 详情</div>
      <table style="width:100%;border-collapse:collapse;font-size:13px;" id="memory-agent-table">
        <thead><tr style="border-bottom:1px solid rgba(255,255,255,0.08);">
          <th style="padding:8px 12px;text-align:left;color:rgba(255,255,255,0.5);" data-i18n="memory.table_agent">Agent</th>
          <th style="padding:8px 12px;text-align:left;color:rgba(255,255,255,0.5);" data-i18n="memory.table_memories">记忆条数</th>
          <th style="padding:8px 12px;text-align:left;color:rgba(255,255,255,0.5);" data-i18n="memory.table_sessions">会话数</th>
          <th style="padding:8px 12px;text-align:left;color:rgba(255,255,255,0.5);" data-i18n="memory.table_last">最后活跃</th>
          <th style="padding:8px 12px;text-align:left;color:rgba(255,255,255,0.5);">类型</th>
        </tr></thead>
        <tbody id="memory-agent-tbody"><tr><td colspan="5" style="padding:20px;text-align:center;color:rgba(255,255,255,0.3);" data-i18n="memory.loading">加载中...</td></tr></tbody>
      </table>
    </div>
  </div>

  <!-- 📊 老化列表 -->
  <div id="tab-aging" style="padding:20px;">
    <div style="font-size:18px;font-weight:600;margin-bottom:16px;" data-i18n="aging.title">📊 知识老化列表</div>
    <div style="display:flex;gap:14px;flex-wrap:wrap;margin-bottom:20px;">
      <div id="aging-total" class="stat-card" style="background:rgba(255,255,255,0.03);border-radius:10px;padding:20px;border:1px solid rgba(255,255,255,0.06);min-width:120px;flex:1;">
        <div style="font-size:28px;font-weight:700;color:#7dd3fc;">-</div>
        <div style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:4px;" data-i18n="aging.scanned">已扫描</div>
      </div>
      <div id="aging-notice" class="stat-card" style="background:rgba(255,255,255,0.03);border-radius:10px;padding:20px;border:1px solid rgba(255,255,255,0.06);min-width:120px;flex:1;">
        <div style="font-size:28px;font-weight:700;color:#fbbf24;">-</div>
        <div style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:4px;" data-i18n="aging.notice">🟡 注意</div>
      </div>
      <div id="aging-aging" class="stat-card" style="background:rgba(255,255,255,0.03);border-radius:10px;padding:20px;border:1px solid rgba(255,255,255,0.06);min-width:120px;flex:1;">
        <div style="font-size:28px;font-weight:700;color:#fb923c;">-</div>
        <div style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:4px;" data-i18n="aging.aging_label">🟠 老化</div>
      </div>
      <div id="aging-stale" class="stat-card" style="background:rgba(255,255,255,0.03);border-radius:10px;padding:20px;border:1px solid rgba(255,255,255,0.06);min-width:120px;flex:1;">
        <div style="font-size:28px;font-weight:700;color:#f87171;">-</div>
        <div style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:4px;" data-i18n="aging.stale">🔴 陈旧</div>
      </div>
    </div>
    <div style="background:rgba(255,255,255,0.03);border-radius:10px;padding:6px 8px;border:1px solid rgba(255,255,255,0.06);margin-bottom:20px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
        <div style="font-size:12px;font-weight:600;color:rgba(255,255,255,0.8);" data-i18n="aging.distribution">老化等级分布</div>
        <div style="display:flex;gap:8px;">
          <button class="compile-btn" onclick="applyAgingFlags()" style="padding:6px 16px;font-size:12px;" data-i18n="aging.batch_mark">🏷 批量标记 aging</button>
          <button class="compile-btn" onclick="location.href='/api/kb/aging/archive-suggestions'" style="padding:6px 16px;font-size:12px;" data-i18n="aging.archive">📦 建议归档</button>
        </div>
      </div>
      <canvas id="aging-pie-chart" width="80" height="80" style="display:block;margin:0 auto;"></canvas>
    </div>
    <div style="background:rgba(255,255,255,0.03);border-radius:10px;padding:20px;border:1px solid rgba(255,255,255,0.06);">
      <div style="font-size:14px;font-weight:600;margin-bottom:12px;color:rgba(255,255,255,0.8);" data-i18n="aging.ranking">老化排行榜（最高分）</div>
      <table style="width:100%;border-collapse:collapse;font-size:13px;" id="aging-top-table">
        <thead><tr style="border-bottom:1px solid rgba(255,255,255,0.08);">
          <th style="padding:8px 12px;text-align:left;color:rgba(255,255,255,0.5);">#</th>
          <th style="padding:8px 12px;text-align:left;color:rgba(255,255,255,0.5);" data-i18n="aging.table_file">文件</th>
          <th style="padding:8px 12px;text-align:left;color:rgba(255,255,255,0.5);" data-i18n="aging.table_score">分数</th>
          <th style="padding:8px 12px;text-align:left;color:rgba(255,255,255,0.5);" data-i18n="aging.table_tier">等级</th>
          <th style="padding:8px 12px;text-align:left;color:rgba(255,255,255,0.5);" data-i18n="aging.table_time">时间衰减</th>
          <th style="padding:8px 12px;text-align:left;color:rgba(255,255,255,0.5);" data-i18n="aging.table_freq">频率</th>
          <th style="padding:8px 12px;text-align:left;color:rgba(255,255,255,0.5);" data-i18n="aging.table_confidence">置信度</th>
        </tr></thead>
        <tbody id="aging-top-tbody"><tr><td colspan="7" style="padding:20px;text-align:center;color:rgba(255,255,255,0.3);" data-i18n="memory.loading">加载中...</td></tr></tbody>
      </table>
    </div>
  </div>

  <!-- ⚙ SETTINGS -->
  <div id="tab-settings">
    <div class="settings-wrap">
      <div class="settings-sidebar">
        <div class="settings-sidebar-item active" data-settings-panel="knowledge" data-i18n="settings.knowledge">📚 知识库</div>
        <div class="settings-sidebar-item" data-settings-panel="database" data-i18n="settings.database">🗄️ 数据库</div>
        <div class="settings-sidebar-item" data-settings-panel="model" data-i18n="settings.model">🤖 模型</div>
        <div class="settings-sidebar-item" data-settings-panel="language" data-i18n="settings.language">🌐 语言</div>
        <div class="settings-sidebar-item" data-settings-panel="stats" data-i18n="settings.stats">📊 统计</div>
        <div class="settings-sidebar-item" data-settings-panel="connection" data-i18n="settings.connection">🔗 连接</div>
        <div class="settings-sidebar-item" data-settings-panel="runtime" data-i18n="settings.runtime">📈 指标</div>
        <div class="settings-sidebar-item" data-settings-panel="graphics" data-i18n="settings.graphics">🎮 渲染</div>
      </div>
      <div class="settings-content">
        <div class="settings-panel active" id="settings-knowledge">
          <div class="settings-section-title" data-i18n="settings.knowledge">知识库</div>
          <div class="setting-row"><span class="setting-label" data-i18n="settings.kb_path">知识库路径</span><span class="setting-value"><code>~/taichu/knowledge/wiki/</code></span></div>
          <div class="setting-row"><span class="setting-label" data-i18n="settings.store_path">存储路径</span><span class="setting-value"><code>~/taichu/storage/raw/</code></span></div>
          <div class="setting-row"><span class="setting-label" data-i18n="settings.api_service">API 服务</span><span class="setting-value"><code>http://127.0.0.1:8765</code></span></div>
          <div class="setting-row"><span class="setting-label" data-i18n="settings.search_engine">搜索引擎</span><span class="setting-value"><code>MemoryRuntime + ChromaDB</code></span></div>
        </div>
        <div class="settings-panel" id="settings-database">
          <div class="settings-section-title" data-i18n="settings.db_index">数据库索引</div>
          <div class="setting-row"><span class="setting-label" data-i18n="settings.chroma_status">ChromaDB</span><span class="setting-value" id="set-chroma-status"><span style="color:rgba(255,255,255,0.3);">● 检测中...</span></span></div>
          <div class="setting-row"><span class="setting-label" data-i18n="settings.vector_count">向量索引数</span><span class="setting-value" id="set-chroma-count">--</span></div>
          <div class="setting-row"><span class="setting-label" data-i18n="settings.index_collections">索引集合</span><span class="setting-value" id="set-chroma-cols">--</span></div>
        </div>
        <div class="settings-panel" id="settings-model">
          <div class="settings-section-title" data-i18n="settings.ai_model">AI 模型</div>
          <div id="model-panel" style="font-size:13px;"><div style="color:rgba(255,255,255,0.3);font-style:italic;" data-i18n="common.loading">加载中...</div></div>
        </div>
        <div class="settings-panel" id="settings-language">
          <div class="settings-section-title" data-i18n="settings.lang_title">语言 / Language</div>
          <div class="setting-row"><span class="setting-label" data-i18n="settings.ui_lang">界面语言</span><span class="setting-value"><select id="lang-select" style="padding:4px 8px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:4px;color:#fff;font-size:12px;outline:none;cursor:pointer;"><option value="zh" style="background:#1a1a2e;color:#fff;">中文</option><option value="en" style="background:#1a1a2e;color:#fff;">English</option></select><button id="lang-confirm" style="margin-left:8px;padding:4px 12px;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);border-radius:4px;color:#fff;font-size:12px;cursor:pointer;" data-i18n="common.confirm">确认</button></span></div>
        </div>
        <div class="settings-panel" id="settings-stats">
          <div class="settings-section-title" data-i18n="settings.file_stats">文件统计</div>
          <div class="setting-row"><span class="setting-label" data-i18n="stats.wiki">Wiki 词条</span><span class="setting-value" id="set-wiki-count">--</span></div>
          <div class="setting-row"><span class="setting-label" data-i18n="stats.archive">归档文件</span><span class="setting-value" id="set-archive-count">--</span></div>
          <div class="setting-row"><span class="setting-label" data-i18n="stats.total">总计</span><span class="setting-value" id="set-total-count">--</span></div>
        </div>
        <div class="settings-panel" id="settings-connection">
          <div class="settings-section-title" data-i18n="settings.conn_status">连接状态</div>
          <div class="setting-row"><span class="setting-label" data-i18n="settings.api_conn">API 服务</span><span class="setting-value" id="set-api-status"><span style="color:rgba(255,255,255,0.3);">● 检测中...</span></span></div>
          <div class="setting-row"><span class="setting-label" data-i18n="settings.ws_conn">WebSocket</span><span class="setting-value" id="set-ws-status"><span style="color:rgba(255,255,255,0.3);">● 离线</span></span></div>
        </div>
        <div class="settings-panel" id="settings-runtime">
          <div class="settings-section-title" data-i18n="settings.runtime_metrics">运行指标</div>
          <div id="settings-metrics">
            <div style="color:rgba(255,255,255,0.3);font-style:italic;font-size:12px;" data-i18n="common.loading">加载中...</div>
          </div>
        </div>
        <div class="settings-panel" id="settings-graphics">
          <div class="settings-section-title" data-i18n="settings.render_quality">渲染画质</div>
          <div id="gfx-panel"></div>
        </div>
      </div>
    </div>
  </div>

</div>
<script src="/static/kb.js?v=11"></script>
</body>
</html>"""


# ── FastAPI app ──

app = FastAPI(title="太初知识宇宙 Web UI", version="0.3.0")


@app.on_event("shutdown")
async def _shutdown():
    """释放 EventBus 线程池等资源"""
    bus.shutdown()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8765", "tauri://localhost", "http://localhost:8765", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# 构建可序列化的图谱数据（兼容 vis-network json 格式）
def _build_graph_json() -> dict:
    """返回 {nodes: [{id, label, value, summary, links}, ...], edges: [{from, to}, ...]}"""
    if not ensure_semantic():
        return {"nodes": [], "edges": [], "total_nodes": 0}
    try:
        graph = semantic._ensure_graph()
    except Exception as e:
        logger.error("[错误] _ensure_graph 失败: %s", e)
        return {"nodes": [], "edges": [], "total_nodes": 0}
    nodes = []
    for n in graph["nodes"]:
        nodes.append(
            {
                "id": n.id,
                "label": n.title,
                "value": max(1, len(n.links)),
                "summary": n.summary or (n.content[:200] if n.content else ""),
                "links": n.links,
            }
        )
    edges = []
    for e in graph["edges"]:
        edges.append({"from": e.source, "to": e.target})
    return {"nodes": nodes, "edges": edges, "total_nodes": len(nodes)}


def _scan_wiki_files():
    """扫描 wiki 目录，返回 {wiki_files, archived_files, wiki_count, archived_count}"""
    wiki_dir = paths.wiki_dir
    archived_dir = wiki_dir / "_archived"

    wiki_files = sorted([f.stem for f in wiki_dir.glob("*.md") if f.stem != "index"]) if wiki_dir.exists() else []
    archived_files = (
        sorted([str(f.relative_to(wiki_dir)) for f in archived_dir.rglob("*.md") if f.stem != "index"])
        if archived_dir.exists()
        else []
    )

    return {
        "wiki_files": wiki_files,
        "archived_files": archived_files,
        "wiki_count": len(wiki_files),
        "archived_count": len(archived_files),
    }


def _lookup_confidence(title: str):
    """Look up confidence for a wiki entry by title. Returns dict or None."""
    if compute_confidence is None:
        return None
    try:
        fp = paths.wiki_dir / f"{title}.md"
        if fp.exists():
            return compute_confidence(fp)
    except Exception as e:
        logger.debug("_compute_confidence failed for %s: %s", title, e)
    return None


def _enrich_result(title: str) -> dict:
    """Read a wiki file and return enriched fields: type, tags, summary."""
    result = {"type": "note", "tags": [], "summary": ""}
    try:
        fp = paths.wiki_dir / f"{title}.md"
        if not fp.exists():
            return result
        # Frontmatter
        if parse_frontmatter is not None:
            fm = parse_frontmatter(fp)
            if fm:
                result["type"] = fm.get("type", "note")
                result["tags"] = fm.get("tags", [])
        # Summary: first 120 chars of body after frontmatter
        text = fp.read_text(encoding="utf-8")
        body = text
        if text.startswith("---"):
            idx = text.find("\n---", 3)
            if idx != -1:
                body = text[idx + 4 :]
        # Remove blank lines at the start
        body = body.strip()
        if body:
            result["summary"] = body[:120]
    except Exception as e:
        logger.debug("_enrich_result failed for %s: %s", title, e)
    return result


def _build_search_results(titles, scores=None):
    """Build results array with confidence info for each title."""
    results = []
    for i, title in enumerate(titles):
        score = scores[i] if scores else 0.0
        item = {
            "title": title,
            "url": title,
            "score": score,
        }
        conf = _lookup_confidence(title)
        if conf is not None:
            item["confidence"] = conf
        # Enrich with frontmatter data (type, tags, summary)
        enriched = _enrich_result(title)
        item.update(enriched)
        results.append(item)
    return results


# ── 主页 ──


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return PAGE_HTML


# ── 统计 ──


@app.get("/api/stats")
async def api_stats() -> dict[str, Any]:
    """返回知识库统计信息：词条数、归档数、ChromaDB 状态"""
    scanned = _scan_wiki_files()
    # ChromaDB 信息
    chroma_ok = False
    chroma_count = 0
    chroma_collections = []
    ensure_memory()
    if memory is not None:
        try:
            store = memory._get_store()
            chroma_ok = True
            chroma_count = store.count
            try:
                chroma_collections = [c.name for c in store.client.list_collections()]
            except Exception as e:
                logger.debug("Failed to list ChromaDB collections: %s", e)
                chroma_collections = ["taichu_memory"]
        except Exception as e:
            logger.debug("Health check ChromaDB access failed: %s", e)
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


@app.get("/api/metrics")
async def api_metrics() -> dict[str, Any]:
    """返回运行时指标：检索统计、图谱结构、记忆数量"""
    try:
        from runtime.metrics.collector import metrics_collector
        from runtime.metrics.counters import metrics_counters

        summary = metrics_collector.summary()

        if not ensure_semantic():
            return {"error": "semantic runtime not available"}
        graph = semantic._ensure_graph()
        nodes = graph["nodes"]
        edges = graph["edges"]
        adj = semantic.adjacency

        orphan = sum(1 for n in nodes if len(adj.get(n.id, set())) == 0)
        avg_nbr = sum(len(v) for v in adj.values()) / len(adj) if adj else 0

        return {
            "retrieval": summary,
            "graph": {
                "nodes": len(nodes),
                "edges": len(edges),
                "orphan_nodes": orphan,
                "avg_neighbors": round(avg_nbr, 2),
            },
            "memory": {"wiki_count": len(list(paths.wiki_dir.glob("*.md")))},
            "runtime": {"eventbus_emits": metrics_counters.get("eventbus.total_emits")},
            "counters": metrics_counters.snapshot(),
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/pipeline/trace")
async def pipeline_trace(q: str = "transformer attention", context: int = 0) -> dict[str, Any]:
    """运行一次 Retrieval Pipeline，返回各阶段耗时"""
    try:
        import asyncio

        from runtime.retrieval import run_retrieval_pipeline

        ctx, docs = await run_retrieval_pipeline(q)

        # 从 runtime_tracer 取各阶段耗时
        from runtime.metrics.tracing import runtime_tracer

        timers = {}
        total_ms = 0
        for node in runtime_tracer.root_nodes:
            if hasattr(node, "children"):
                for child in node.children or []:
                    timers[child.name] = round(child.duration_ms(), 2)
            if node.name == "retrieval_pipeline":
                total_ms = round(node.duration_ms(), 2)

        graph_nodes = sum(len(d.get("graph_neighbors", [])) for d in docs)

        result = {
            "timers": timers,
            "total_ms": total_ms,
            "result_count": len(docs),
            "graph_nodes_expanded": graph_nodes,
            "query": q,
        }
        if context:
            result["context"] = ctx
        return result
    except Exception as e:
        logger.error(f"[pipeline_trace] 检索管道执行失败: {e}")
        return {"error": str(e)}


# ── 图谱 ──


@app.get("/api/kb/graph")
async def kb_graph(limit: int = 150, expand: str = "") -> dict[str, Any]:
    """返回知识图谱数据，支持 top-N 核心节点或单节点邻域展开模式"""
    graph_data = _build_graph_json()

    if expand:
        # 单节点扩展模式
        expand_nodes = set(expand.split(","))
        connected_edges = [e for e in graph_data["edges"] if e["from"] in expand_nodes or e["to"] in expand_nodes]
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
        "edges": [e for e in graph_data["edges"] if e["from"] in top_ids and e["to"] in top_ids],
        "total_nodes": graph_data["total_nodes"],
        "mode": "core",
    }


# ── 搜索（兼容旧前端格式）──


@app.get("/api/kb/search")
async def kb_search(q: str = "", mode: str = "search", min_confidence: float = 0.0) -> dict[str, Any]:
    """语义搜索 — 降级链: 豆包 embedding → ChromaDB MemoryRuntime"""
    if not q:
        return {"results": [], "error": "请输入搜索词"}

    # 降级链: 豆包 embedding → ChromaDB (MemoryRuntime) → 结束
    import contextlib
    import io

    # 第一优先：尝试豆包 embedding
    try:
        kb_mod = _load_kb_models()
        if kb_mod is None:
            raise ImportError("kb_models 加载失败")
        # 重定向 stdout
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            kb_mod.cmd_search(q)
        output = f.getvalue().strip()
        if output and "❌" not in output:
            # Parse [[title]] from doubao output text
            titles = re.findall(r"\[\[(.+?)\]\]", output)
            results = _build_search_results(titles)
            if min_confidence > 0:
                results = [r for r in results if r.get("confidence", {}).get("score", 0) >= min_confidence]
            return {"query": q, "mode": mode, "output": output, "engine": "doubao_embedding", "results": results}
    except Exception as e:
        logger.warning(f"[搜索] 豆包 embedding 失败，降级 ChromaDB: {e}")
        pass

    # 第二优先：降级到 ChromaDB MemoryRuntime
    try:
        _memory = get_memory()
        raw_results = _memory.search(q, top_k=5)
        if raw_results:
            lines = [f"  {i+1}. [[{r['title']}]] (score: {r['score']:.4f})" for i, r in enumerate(raw_results)]
            output = (
                f"Semantic search: {q}\\n\\n  Engine: ChromaDB (fallback)\\n  Results: {len(raw_results)}\\n\\n"
                + "\\n".join(lines)
            )
            results = _build_search_results([r["title"] for r in raw_results], scores=[r["score"] for r in raw_results])
            if min_confidence > 0:
                results = [r for r in results if r.get("confidence", {}).get("score", 0) >= min_confidence]
            return {"query": q, "mode": mode, "output": output, "engine": "chromadb_fallback", "results": results}
    except Exception as e:
        logger.error(f"[搜索] ChromaDB 降级也失败: {e}")

    return {"query": q, "mode": mode, "output": "(无匹配结果)", "engine": "none", "results": []}


@app.get("/api/kb/ask")
async def kb_ask(q: str = "") -> dict[str, Any]:
    """AI 问答 — 降级链: 豆包 RAG → ChromaDB 搜索 + 结果拼接"""
    if not q:
        return {"error": "请输入问题"}

    # 降级链: 豆包 RAG → ChromaDB + 简单拼接 → 结束
    import contextlib
    import io

    km = str(paths.kb_models)

    # 第一优先：尝试豆包 RAG
    try:
        kb_mod = _load_kb_models()
        if kb_mod is None:
            raise ImportError("kb_models 加载失败")
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            kb_mod.cmd_ask(q)
        output = f.getvalue().strip()
        if output and "❌" not in output:
            return {"query": q, "raw_output": output, "engine": "doubao_rag"}
    except Exception as e:
        logger.debug("Doubao RAG ask failed, falling back: %s", e)

    # 第二优先：降级到 ChromaDB 搜索 + 简单结果拼接
    try:
        _memory = get_memory()
        results = _memory.search(q, top_k=3)
        if results:
            lines = [f"找到 {len(results)} 条相关结果（ChromaDB 降级）\\n"]
            for i, r in enumerate(results):
                preview = r.get("text", "")[:200]
                lines.append(f"{i+1}. [[{r['title']}]] — {preview}")
            answer = "\\n".join(lines)
            return {"query": q, "raw_output": answer, "engine": "chromadb_fallback"}
    except Exception as e:
        logger.debug("ChromaDB fallback ask failed: %s", e)

    return {"query": q, "raw_output": "(无匹配结果)", "engine": "none"}


@app.post("/api/kb/search/feedback")
async def kb_search_feedback(request: Request) -> dict[str, Any]:
    """Receive search result feedback (placeholder for future learning)."""
    body = await request.json()
    title = body.get("title", "")
    helpful = body.get("helpful", False)
    logger.info("[搜索反馈] title=%s, helpful=%s", title, helpful)
    return {"ok": True}


# ── 待处理文件 ──


@app.get("/api/kb/pending")
async def kb_pending() -> dict[str, Any]:
    """列出 inbox 目录中待编译的文件"""
    inbox_dir = paths.inbox_dir
    files = []
    if inbox_dir.exists():
        for f in sorted(inbox_dir.iterdir()):
            if f.is_dir() or f.suffix == ".md":
                continue
            files.append(
                {
                    "name": f.name,
                    "size": f.stat().st_size,
                    "modified": f.stat().st_mtime,
                }
            )
    return {"pending": files, "count": len(files)}


@app.post("/api/kb/pending/delete")
async def kb_pending_delete(request: Request) -> dict[str, Any]:
    """删除指定待处理文件（从 inbox 和 raw 目录移除）"""
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
async def kb_compile() -> dict[str, Any]:
    """触发 doubao_manager.py 编译 inbox 中所有待处理文件"""
    doubao = paths.get("tools") / "doubao_manager.py"
    if not doubao.exists():
        return {"ok": False, "error": "doubao_manager.py 不存在"}

    # 校验编译模型配置完整性（不发起 HTTP 请求，避免无认证头导致误判）
    from config.models import models as _models

    _cfg = _models.get("compile")
    if not _cfg.get("api_key") or not _cfg.get("base_url"):
        return {
            "ok": False,
            "error": "LLM 编译模型未配置（api_key / base_url 缺失）",
            "converted": 0,
        }

    try:
        result = subprocess.run(
            [sys.executable, str(doubao)],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(paths.root),
        )
        output = result.stdout.strip()
        converted = 0
        if "CONVERTED:" in output:
            converted = int(output.split("CONVERTED:")[-1].split("\n")[0])
        # 编译完成后刷新语义图谱
        if result.returncode == 0 and converted > 0:
            if ensure_semantic():
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
async def upload(files: list[UploadFile] = File(...)) -> dict[str, Any]:
    """上传文件到知识库：.md 直接发布到 wiki，其他格式送入 inbox 待编译"""
    raw_dir = paths.raw_dir
    inbox_dir = paths.inbox_dir
    wiki_dir = paths.wiki_dir
    store_dir = paths.get("storage", "raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    inbox_dir.mkdir(parents=True, exist_ok=True)
    wiki_dir.mkdir(parents=True, exist_ok=True)
    store_dir.mkdir(parents=True, exist_ok=True)

    uploaded_md, uploaded_other, uploaded_stored = 0, 0, 0
    for f in files:
        ext = Path(f.filename).suffix.lower()
        if ext not in SUPPORTED_EXT:
            continue
        content = await f.read()
        raw_target = raw_dir / f.filename
        with open(raw_target, "wb") as wf:
            wf.write(content)
        # 存入统一存储（哈希去重）
        from ingest.pipelines import store_file

        _ = store_file(raw_target, store_dir)
        uploaded_stored += 1
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
        parts.append(f"{uploaded_other} 个文件待编译")
    return {
        "ok": True,
        "md_count": uploaded_md,
        "other_count": uploaded_other,
        "stored_count": uploaded_stored,
        "compiled": False,
        "note": "；".join(parts) if parts else "没有文件被上传",
    }


@app.post("/compile")
async def compile_check() -> dict[str, Any]:
    """已弃用的编译入口，保留用于向后兼容"""
    return {"ok": True, "count": 0, "pending": [], "note": "已弃用，请使用上传面板自动编译"}


@app.get("/health")
async def health() -> dict[str, Any]:
    """健康检查端点"""
    return {"status": "ok"}


# ── 模型管理 ──


@app.get("/api/models")
async def list_models() -> dict[str, Any]:
    """返回当前模型配置 + 可用提供商列表（隐藏 API key）"""
    import yaml

    from config.models import models as _models
    from config.paths import paths as _paths

    # 当前活跃模型（隐藏 API key）
    current = {}
    for role in ["compile", "query", "reasoning", "embedding", "vision"]:
        try:
            cfg = _models.get(role)
            current[role] = {
                "provider": cfg.get("provider", ""),
                "model": cfg.get("model", ""),
                "purpose": cfg.get("purpose", ""),
            }
        except Exception as e:
            logger.warning("Failed to read model config for %s: %s", role, e)
            current[role] = {"provider": "", "model": "", "purpose": ""}

    # 读取原始 YAML 获取 providers 列表
    yaml_path = _paths.root / "config" / "models.yaml"
    providers = []
    try:
        with open(yaml_path, "r") as f:
            raw = yaml.safe_load(f)
        if raw and "providers" in raw:
            for p in raw["providers"]:
                providers.append(
                    {
                        "id": p.get("id"),
                        "name": p.get("name"),
                        "doc": p.get("doc", ""),
                        "api_key_from": p.get("api_key_from", ""),
                        "base_url": p.get("base_url", ""),
                        "chat_endpoint": p.get("chat_endpoint", ""),
                        "embed_endpoint": p.get("embed_endpoint", ""),
                        "models": p.get("models", {}),
                    }
                )
    except Exception as e:
        logger.warning("Failed to read model providers from YAML: %s", e)

    return {"current": current, "providers": providers}


_ROLE_MODEL_KEYS = {
    "reasoning": ["llm_reasoning", "llm", "compile"],
    "embedding": ["embedding"],
    "vision": ["vision"],
    "compile": ["compile", "llm"],
    "query": ["llm_fast", "llm", "compile"],
}


@app.post("/api/models/switch")
async def switch_provider(req: Request) -> dict[str, Any]:
    """切换到指定提供商。role 指定仅切换该角色（reasoning/embedding/vision），不传则切换全部。"""
    import yaml

    from config.paths import paths as _paths

    body = await req.json()
    provider_id = body.get("provider_id", "").strip()
    api_key = body.get("api_key", "").strip()
    role = body.get("role", "").strip()
    if not provider_id:
        return {"ok": False, "error": "请指定提供商"}

    yaml_path = _paths.root / "config" / "models.yaml"
    try:
        with open(yaml_path, "r") as f:
            raw = yaml.safe_load(f)
    except Exception as e:
        return {"ok": False, "error": f"读取配置失败: {e}"}

    if not raw or "providers" not in raw:
        return {"ok": False, "error": "配置文件中无 providers 列表"}

    # 查找目标提供商
    target = None
    for p in raw["providers"]:
        if p.get("id") == provider_id:
            target = p
            break
    if not target:
        return {"ok": False, "error": f"未找到提供商: {provider_id}"}

    # 更新 API 配置（全局）
    base_url = body.get("base_url", "").strip()
    endpoint = body.get("endpoint", "").strip()
    if base_url:
        raw["api"]["base_url"] = base_url
    elif target.get("base_url"):
        raw["api"]["base_url"] = target["base_url"]
    if endpoint:
        raw["api"]["chat_endpoint"] = endpoint
    if api_key:
        raw["api"]["api_key"] = api_key

    pm = target.get("models", {}) or {}

    def _resolve_model(role_name: str) -> str | None:
        for key in _ROLE_MODEL_KEYS.get(role_name, []):
            if key in pm:
                return pm[key]
        return None

    if role:
        # 单角色切换
        if role not in raw["models"]:
            return {"ok": False, "error": f"未知角色: {role}"}
        model_id = _resolve_model(role)
        if not model_id:
            return {"ok": False, "error": f"提供商 {target.get('name')} 未提供 {role} 模型"}
        raw["models"][role]["provider"] = provider_id
        raw["models"][role]["model"] = model_id
        changed = [role]
    else:
        # 全量切换（向后兼容）
        active_roles = ["compile", "query", "reasoning", "embedding", "vision"]
        role_model_map = {}
        for r in active_roles:
            m = _resolve_model(r)
            if m:
                role_model_map[r] = m
        for r in active_roles:
            if r in raw["models"] and r in role_model_map:
                raw["models"][r]["provider"] = provider_id
                raw["models"][r]["model"] = role_model_map[r]
        changed = list(role_model_map.keys())

    # 写回 YAML（先备份）
    try:
        backup = yaml_path.with_suffix(".yaml.bak")
        if yaml_path.exists():
            import shutil

            shutil.copy2(yaml_path, backup)
        with open(yaml_path, "w") as f:
            yaml.dump(raw, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    except Exception as e:
        return {"ok": False, "error": f"写入配置失败: {e}"}

    return {"ok": True, "message": f"已切换 {', '.join(changed)} 到 {target.get('name', provider_id)}"}


connected_clients: list[WebSocket] = []


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    """WebSocket 端点：接受客户端连接，响应 ping/pong，广播事件"""
    await ws.accept()
    connected_clients.append(ws)
    logger.info(f"[WS] 客户端连接: {len(connected_clients)} 个")

    try:
        while True:
            data = await ws.receive_text()
            if data == "ping":
                await ws.send_text("pong")
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.warning(f"[WS] 错误: {e}")
    finally:
        if ws in connected_clients:
            connected_clients.remove(ws)


async def _ws_broadcast(event: str, data: dict):
    """广播事件到所有 WebSocket 客户端"""
    payload = json.dumps({"event": event, "data": data})
    dead = []
    for ws in connected_clients:
        try:
            await ws.send_text(payload)
        except Exception as e:
            logger.debug("WebSocket broadcast failed, marking dead: %s", e)
            dead.append(ws)
    for ws in dead:
        if ws in connected_clients:
            connected_clients.remove(ws)


# 注册事件总线 → WebSocket 广播
register_ws_handlers(_ws_broadcast)


# ── 知识库置信度 ──


@app.get("/api/kb/confidence")
async def kb_confidence(file: str = "") -> dict[str, Any]:
    """Get confidence score for a single file or all files in the wiki."""
    wiki_dir = paths.wiki_dir
    if file:
        fp = wiki_dir / f"{file}.md"
        if not fp.exists():
            return {"error": "File not found"}
        if compute_confidence is None:
            return {"error": "Confidence module not available"}
        return compute_confidence(fp)
    # Return all scores
    if batch_confidence is None:
        return {"error": "Confidence module not available"}
    scores = batch_confidence(wiki_dir)
    return {"scores": scores}


# ── 知识老化检测 ──


@app.get("/api/kb/aging")
async def kb_aging(min_score: float = 0, limit: int = 0, tier: str = "") -> dict[str, Any]:
    """Get aging scores for all wiki articles.

    Args:
        min_score: Minimum aging score filter (0.0–1.0).
        limit: Max results (0 = unlimited).
        tier: Filter by tier ("active", "notice", "aging", "stale").
    """
    if batch_aging is None:
        return {"error": "Aging module not available"}
    results = batch_aging(min_score=min_score, limit=limit)
    if tier:
        results = [r for r in results if r["tier"] == tier]
    return {"results": results}


@app.get("/api/kb/aging/report")
async def kb_aging_report() -> dict[str, Any]:
    """Get aging statistics summary (tier distribution, counts)."""
    if aging_report is None:
        return {"error": "Aging module not available"}
    return aging_report()


@app.get("/api/kb/aging/review")
async def kb_aging_review() -> dict[str, Any]:
    """List articles in notice/aging tiers needing review."""
    if suggest_review is None:
        return {"error": "Aging module not available"}
    return {"results": suggest_review()}


@app.get("/api/kb/aging/archive-suggestions")
async def kb_aging_archive(min_score: float = 0.7) -> dict[str, Any]:
    """List stale articles as archive candidates."""
    if suggest_archive is None:
        return {"error": "Aging module not available"}
    return {"results": suggest_archive(min_score=min_score)}


@app.get("/api/kb/aging/events")
async def kb_aging_events(limit: int = 50) -> dict[str, Any]:
    """Read recent aging event log entries."""
    if get_aging_events is None:
        return {"error": "Aging module not available"}
    return {"events": get_aging_events(limit=limit)}


@app.post("/api/kb/aging/apply")
async def kb_aging_apply(file: str = "") -> dict[str, Any]:
    """Apply aging flags to frontmatter.

    If file is specified, flag only that file.
    Otherwise scan all wiki files.
    """
    if apply_all_flags is None:
        return {"error": "Aging module not available"}
    wiki_dir = paths.wiki_dir
    if file:
        fp = wiki_dir / f"{file}.md"
        if not fp.exists():
            return {"error": "File not found"}
        return apply_aging_flag(fp)
    results = apply_all_flags()
    flagged = sum(1 for r in results if r.get("action") == "flagged")
    return {"total": len(results), "flagged": flagged, "results": results}


# ── Agent 注册/心跳检测 ──

_agent_registry = {}  # agent_id -> {"type": str, "meta": dict, "last_heartbeat": float}
HEARTBEAT_TIMEOUT = 60  # 秒，超过此时间未心跳视为离线


@app.post("/api/agents/register")
async def agent_register(request: Request) -> dict[str, Any]:
    """Agent 注册。外部 Agent 调用此接口告知系统自己的存在。

    Body:
        agent_id: Agent 标识（必填）
        type: Agent 类型（可选，如 retrieval/memory/synthesizer/claude-code）
        meta: 附加信息（可选，如版本、能力描述等）
    """
    body = await request.json()
    agent_id = body.get("agent_id", "").strip()
    if not agent_id:
        return {"error": "agent_id is required"}
    agent_type = body.get("type", "external")
    meta = body.get("meta", {})
    _agent_registry[agent_id] = {
        "agent_id": agent_id,
        "type": agent_type,
        "meta": meta,
        "last_heartbeat": time.time(),
    }
    # 创建 agent 专属目录
    if on_agent_registered is not None:
        on_agent_registered(agent_id, agent_type, meta)
    return {"status": "registered", "agent_id": agent_id}


@app.post("/api/agents/heartbeat")
async def agent_heartbeat(request: Request) -> dict[str, Any]:
    """Agent 心跳。定期调用以维持在线状态。

    Body:
        agent_id: Agent 标识（必填）
    """
    body = await request.json()
    agent_id = body.get("agent_id", "").strip()
    if not agent_id:
        return {"error": "agent_id is required"}
    now = time.time()
    if agent_id in _agent_registry:
        _agent_registry[agent_id]["last_heartbeat"] = now
    else:
        # 未注册但发心跳，自动注册
        _agent_registry[agent_id] = {
            "agent_id": agent_id,
            "type": body.get("type", "external"),
            "meta": body.get("meta", {}),
            "last_heartbeat": now,
        }
    return {"status": "ok", "agent_id": agent_id}


@app.get("/api/agents")
async def agent_list() -> dict[str, Any]:
    """返回所有已注册 Agent 及其在线状态。

    在线判定：心跳时间不超过 HEARTBEAT_TIMEOUT 秒。
    """
    now = time.time()
    agents = []
    for aid, info in _agent_registry.items():
        elapsed = now - info["last_heartbeat"]
        agents.append(
            {
                "agent_id": aid,
                "type": info["type"],
                "meta": info.get("meta", {}),
                "online": elapsed < HEARTBEAT_TIMEOUT,
                "last_seen": info["last_heartbeat"],
            }
        )
    return {"agents": agents, "total": len(agents)}


# ── Agent 文件管理（profile / personality / sessions）──


@app.get("/api/agents/{agent_id}/profile")
async def agent_get_profile(agent_id: str) -> dict[str, Any]:
    """获取 Agent 的 profile.yaml 内容。"""
    if _agent_file_mgr is None:
        return {"error": "Agent file manager not available"}
    profile = _agent_file_mgr.get_profile(agent_id)
    if profile is None:
        return {"error": "Agent not found", "agent_id": agent_id}
    return {"agent_id": agent_id, "profile": profile}


@app.put("/api/agents/{agent_id}/profile")
async def agent_update_profile(agent_id: str, request: Request) -> dict[str, Any]:
    """更新 Agent profile（合并到 profile.yaml）。"""
    if _agent_file_mgr is None:
        return {"error": "Agent file manager not available"}
    body = await request.json()
    profile = _agent_file_mgr.update_profile(agent_id, body)
    if profile is None:
        return {"error": "Agent not found", "agent_id": agent_id}
    return {"agent_id": agent_id, "profile": profile}


@app.get("/api/agents/{agent_id}/personality")
async def agent_get_personality(agent_id: str) -> dict[str, Any]:
    """获取 Agent 的 personality.md 内容。"""
    if _agent_file_mgr is None:
        return {"error": "Agent file manager not available"}
    content = _agent_file_mgr.get_personality(agent_id)
    if content is None:
        return {"error": "Agent not found", "agent_id": agent_id}
    return {"agent_id": agent_id, "personality": content}


@app.put("/api/agents/{agent_id}/personality")
async def agent_update_personality(agent_id: str, request: Request) -> dict[str, Any]:
    """更新 Agent 的 personality.md。"""
    if _agent_file_mgr is None:
        return {"error": "Agent file manager not available"}
    body = await request.json()
    content = body.get("content", "")
    if not content:
        return {"error": "content is required"}
    _agent_file_mgr.update_personality(agent_id, content)
    return {"agent_id": agent_id, "status": "updated"}


@app.get("/api/agents/{agent_id}/sessions")
async def agent_list_sessions(agent_id: str) -> dict[str, Any]:
    """列出 Agent 的所有会话日期。"""
    if _agent_file_mgr is None:
        return {"error": "Agent file manager not available"}
    sessions = _agent_file_mgr.list_sessions(agent_id)
    return {"agent_id": agent_id, "sessions": sessions, "total": len(sessions)}


@app.get("/api/agents/{agent_id}/sessions/{date}")
async def agent_get_session(agent_id: str, date: str) -> dict[str, Any]:
    """获取某日的完整会话日志（YYYY-MM-DD）。"""
    if _agent_file_mgr is None:
        return {"error": "Agent file manager not available"}
    content = _agent_file_mgr.get_session(agent_id, date)
    if content is None:
        return {"error": "Session not found", "agent_id": agent_id, "date": date}
    return {"agent_id": agent_id, "date": date, "content": content}


# ── 跨会话记忆 ──


@app.post("/api/kb/memory")
async def memory_save(request: Request) -> dict[str, Any]:
    """保存一条跨会话记忆。

    Body:
        content: 记忆内容（必填）
        agent_id: Agent 标识（默认 taichu）
        session_id: 会话 ID（不传则自动生成）
        type: 类型（conversation/decision/insight/summary/user_preference）
        importance: 重要性 0-1
        summary: 简短摘要
    """
    if get_session_memory is None:
        return {"error": "Session memory module not available"}
    body = await request.json()
    content = body.get("content", "")
    if not content:
        return {"error": "content is required"}
    # 自动注册发请求的 Agent
    agent_id = body.get("agent_id", "taichu")
    if agent_id not in _agent_registry:
        _agent_registry[agent_id] = {
            "agent_id": agent_id,
            "type": body.get("type", "external"),
            "meta": {},
            "last_heartbeat": time.time(),
        }
    sm = get_session_memory()
    mem_id = sm.save(
        content=content,
        agent_id=body.get("agent_id", "taichu"),
        session_id=body.get("session_id", ""),
        memory_type=body.get("type", "conversation"),
        importance=body.get("importance", 0.6),
        summary=body.get("summary", ""),
        metadata=body.get("metadata"),
    )
    # 追加到 agent 当日会话日志
    if on_memory_stored is not None:
        on_memory_stored(
            agent_id=agent_id,
            memory_type=body.get("type", "conversation"),
            content=content,
            session_id=body.get("session_id", ""),
        )
    return {"id": mem_id, "status": "saved"}


@app.get("/api/kb/memory")
async def memory_recall(q: str = "", agent: str = "", limit: int = 10, types: str = "") -> dict[str, Any]:
    """语义检索跨会话记忆。

    Args:
        q: 搜索关键词。
        agent: 限定 Agent（空=搜索所有）。
        limit: 最大结果数。
        types: 限定类型（逗号分隔，如 "decision,insight"）。
    """
    if get_session_memory is None:
        return {"error": "Session memory module not available"}
    if not q:
        return {"results": []}
    sm = get_session_memory()
    type_filter = types.split(",") if types else None
    results = sm.recall(
        query=q,
        agent_id=agent,
        limit=limit,
        memory_types=type_filter,
    )
    return {"results": results}


@app.get("/api/kb/memory/sessions")
async def memory_sessions(agent: str = "", limit: int = 50) -> dict[str, Any]:
    """列出所有 Agent 的跨会话记忆列表。

    Args:
        agent: 限定 Agent（空=所有 Agent）。
        limit: 最大返回数。
    """
    if get_session_memory is None:
        return {"error": "Session memory module not available"}
    sm = get_session_memory()
    sessions = sm.list_sessions(agent_id=agent, limit=limit)
    return {"sessions": sessions}


@app.post("/api/kb/memory/summarize")
async def memory_summarize(request: Request) -> dict[str, Any]:
    """将某次会话的记忆压缩为一条摘要。

    Body:
        agent_id: Agent 标识（必填）
        session_id: 会话 ID（必填）
        summary: 自定义摘要（不传则自动生成）
    """
    if get_session_memory is None:
        return {"error": "Session memory module not available"}
    body = await request.json()
    agent_id = body.get("agent_id", "")
    session_id = body.get("session_id", "")
    if not agent_id or not session_id:
        return {"error": "agent_id and session_id are required"}
    sm = get_session_memory()
    result = sm.summarize_session(
        agent_id=agent_id,
        session_id=session_id,
        summary_text=body.get("summary", ""),
    )
    return result


# ── 入口 ──


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Taichu KB Web UI (FastAPI)")
    parser.add_argument("port", nargs="?", type=int, default=int(os.environ.get("TAICHU_PORT", 8765)))
    parser.add_argument("--bind", default=os.environ.get("TAICHU_BIND", "0.0.0.0"))
    args = parser.parse_args()
    print(f"太初知识宇宙 Web UI — http://localhost:{args.port}")
    print(f"  知识库: {paths.root}")
    print("  API:    /api/stats /api/kb/graph /api/kb/search /api/kb/pending /api/kb/aging /api/kb/memory")
    uvicorn.run(app, host=args.bind, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
