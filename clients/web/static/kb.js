// ── Tab navigation (Tauri style) ──
const navItems = document.querySelectorAll('.nav-item');
navItems.forEach(function(tab){
  tab.addEventListener('click',function(){
    navItems.forEach(function(t){t.classList.remove('active');});
    tab.classList.add('active');
    const tabId = tab.dataset.tab;
    document.querySelectorAll('#content-area > div').forEach(function(d){d.style.display='none';});
    const content = document.getElementById('tab-'+tabId);
    if(content)content.style.display='block';
    if(tabId==='home'){setTimeout(refreshNebula,50);setTimeout(refreshPending,100);}
    if(tabId==='upload'){setTimeout(refreshPending,100);setTimeout(setUploadListeners,100);setTimeout(refreshStats,50);}
    if(tabId==='entries'){_wikiPage=0;setTimeout(refreshStats,50);}
    if(tabId==='settings'){setTimeout(refreshSettings,100);}
  });
});

// ── Stats refresh (paginated) ──
let _wikiPage = 0;
const _pageSize = 20;
let _lastStats = null;
let _confidenceScores = [];

async function refreshStats() {
  try {
    const resp = await fetch('/api/stats');
    const s = await resp.json();
    _lastStats = s;
    document.getElementById('stats-bar').innerHTML =
      '<div class="stat-card"><div class="num">' + s.total_count + '</div><div class="label">' + __('stats.total') + '</div></div>' +
      '<div class="stat-card"><div class="num">' + s.wiki_count + '</div><div class="label">' + __('stats.core') + '</div></div>' +
      '<div class="stat-card"><div class="num">' + s.archived_count + '</div><div class="label">' + __('stats.archive') + '</div></div>';
    var wBody = document.getElementById('wiki-panel');
    _wikiPage = 0;
    renderWikiPage();
    try {
      var cresp = await fetch('/api/kb/confidence');
      var cdata = await cresp.json();
      _confidenceScores = cdata.scores || [];
    } catch(e) { _confidenceScores = []; }
  } catch (e) { console.error('Stats error:', e); }
}

function renderWikiPage() {
  var s = _lastStats;
  if (!s) return;
  var wBody = document.getElementById('wiki-panel');
  if (!wBody) {
    wBody = document.createElement('div');
    wBody.id = 'wiki-panel';
    document.getElementById('tab-entries').appendChild(wBody);
  }
  const core = s.wiki_articles || [];
  const archived = s.archived_articles || [];
  const start = _wikiPage * _pageSize;
  const total = core.length + archived.length;
  const totalPages = Math.ceil(total / _pageSize) || 1;
  let html = '<div class="wiki-header"><span class="wiki-count">' + total + ' <span class="i18n-count">' + __('entries.count') + '</span></span><span class="wiki-page">' + __('entries.page') + ' ' + (_wikiPage + 1) + '/' + totalPages + ' ' + __('entries.page_total') + '</span></div>';
  for (var i = start; i < start + _pageSize && i < core.length; i++) {
    var name = esc(core[i]).replace(/^archive-/i, '');
    html += '<div class="item"><span class="dot core"></span><span class="name">' + name + '</span>' + getConfBadge(name) + '<span class="tag">' + __('stats.core') + '</span></div>';
  }
  for (var i = Math.max(0, start - core.length); i < start + _pageSize - core.length && i < archived.length; i++) {
    var name = esc(archived[i]).replace(/^archive-/i, '');
    html += '<div class="item"><span class="dot archive"></span><span class="name">' + name + '</span>' + getConfBadge(name) + '<span class="tag">' + __('stats.archived') + '</span></div>';
  }
  if (total > _pageSize) {
    html += '<div class="page-bar">';
    if (_wikiPage > 0) html += '<button onclick="_wikiPage--;renderWikiPage()">' + __('entries.prev') + '</button>';
    if (start + _pageSize < total) html += '<button onclick="_wikiPage++;renderWikiPage()">' + __('entries.next') + '</button>';
    html += '</div>';
  }
  wBody.innerHTML = html;
}

// ── Upload (overview mini + upload tab) ──
function setupUploadZone(dropzoneEl, fileInputEl) {
  if (!dropzoneEl || !fileInputEl) return;
  const dz = dropzoneEl;
  const fi = fileInputEl;
  dz.addEventListener('dragover', e => { e.preventDefault(); dz.classList.add('dragover'); });
  dz.addEventListener('dragleave', () => dz.classList.remove('dragover'));
  dz.addEventListener('drop', e => { e.preventDefault(); dz.classList.remove('dragover'); handleFiles(e.dataTransfer.files); });
  dz.addEventListener('click', () => fi.click());
  fi.addEventListener('change', () => handleFiles(fi.files));
}
// Init overview dropzone
// Init upload tab dropzone (called when tab switches)
function setUploadListeners() {
  setupUploadZone(document.getElementById('dropzone-upload'), document.getElementById('file-input-upload'));
}

async function handleFiles(files) {
  const formData = new FormData();
  let fileCount = 0;
  const allowed = ['.md','.pdf','.docx','.pptx','.html','.htm','.txt','.csv','.xlsx','.epub','.png','.jpg','.jpeg','.webp','.gif','.bmp','.py','.js','.ts','.yaml','.toml'];
  for (const f of files) {
    const ext = '.' + f.name.split('.').pop().toLowerCase();
    if (allowed.includes(ext)) { formData.append('files', f); fileCount++; }
  }
  const fileList = document.getElementById('file-list');
  if (fileList) {
    fileList.innerHTML = '';
    for (const f of files) {
      const ext = '.' + f.name.split('.').pop().toLowerCase();
      if (allowed.includes(ext)) {
        const li = document.createElement('li');
        li.style.cssText = 'padding:3px 0;border-bottom:1px solid rgba(255,255,255,0.04);';
        li.textContent = '📄 ' + f.name + ' (' + (f.size > 1024 ? (f.size/1024).toFixed(1) + 'KB' : f.size + 'B') + ')';
        fileList.appendChild(li);
      }
    }
  }
  if (fileCount === 0) { showResult(__('upload.support_error'), 'error'); return; }
  showLoading(__('upload.uploading') + ' ' + fileCount + '...');
  try {
    const resp = await fetch('/upload', { method: 'POST', body: formData });
    const d = await resp.json();
    hideLoading();
    if (d.ok) {
      showResult(d.note || (__('upload.uploading') + ' ' + d.md_count + ' .md' + (d.other_count ? ' + ' + d.other_count + ' ' + __('upload.pending_unit') : '')), 'success');
      refreshStats(); refreshNebula(); refreshPending();
    } else {
      showResult(__('upload.fail') + (d.error || __('upload.error')), 'error');
    }
  } catch (e) {
    hideLoading();
    showResult(__('upload.error') + e.message, 'error');
  }
}

// ── Pending files + Compile ──
async function refreshPending() {
  try {
    const resp = await fetch('/api/kb/pending');
    const d = await resp.json();
    ['pending-list-upload'].forEach(function(panelId) {
      const panel = document.getElementById(panelId);
      if (!panel) return;
      if (d.count === 0) { panel.innerHTML = '<div class="empty">' + __('upload.empty') + '</div>'; return; }
      let html = '';
      d.pending.forEach(function(f) {
        const sizeStr = f.size > 1024 ? (f.size / 1024).toFixed(1) + 'KB' : f.size + 'B';
        const safeName = esc(f.name);
        html += '<div class="item"><span class="dot pending"></span><span class="name">' + safeName + '</span><span style="font-size:11px;color:rgba(255,255,255,0.5);margin-left:8px;">' + sizeStr + '</span><button onclick="deletePending(\'' + safeName.replace(/'/g, "\\'") + '\')" style="margin-left:auto;background:none;border:none;color:#e8963e;font-size:14px;cursor:pointer;padding:2px 6px;" title="' + __('delete.confirm') + '">\u2715</button></div>';
      });
      panel.innerHTML = html;
    });
  } catch (e) { console.error('Pending error:', e); }
}

async function triggerCompile() {
  // Get initial pending count
  var totalPending = 0;
  try {
    var pr = await fetch('/api/kb/pending');
    var pd = await pr.json();
    totalPending = pd.count;
  } catch(e) {}
  if (totalPending === 0) { showResult(__('compile.none'), 'success'); return; }

  showLoading('⚡ 编译中 0/' + totalPending, 0);
  var startTime = Date.now();

  // Start compile (run in background)
  var compilePromise = fetch('/api/kb/compile', { method: 'POST' });

  // Poll pending count for real progress
  var pollTimer = setInterval(async function() {
    try {
      var pr2 = await fetch('/api/kb/pending');
      var pd2 = await pr2.json();
      var done = totalPending - pd2.count;
      var pct = Math.round((done / totalPending) * 100);
      var elapsed = Math.round((Date.now() - startTime) / 1000);
      showLoading('⚡ 编译中 ' + done + '/' + totalPending + ' · ' + elapsed + 's', pct);
      if (pd2.count === 0) {
        clearInterval(pollTimer);
        hideLoading();
        refreshPending(); refreshStats();
        showResult(__('compile.done') + ' ' + totalPending + ' ' + __('compile.files'), 'success');
      }
    } catch(e) {}
  }, 2000);

  // Wait for compile response
  try {
    var resp = await compilePromise;
    var d = await resp.json();
    if (!d.ok) {
      clearInterval(pollTimer);
      hideLoading();
      showResult(__('upload.compile_fail') + (d.error || __('upload.compile_error')), 'error');
    }
  } catch(e) {
    clearInterval(pollTimer);
    hideLoading();
    showResult(__('upload.compile_error') + e.message, 'error');
  }

  // Safety: stop polling after 5 min
  setTimeout(function() { clearInterval(pollTimer); }, 300000);
}

function showLoading(msg, percent) {
  var overlay = document.getElementById('loading-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.innerHTML =
      '<div style="text-align:center;">' +
        '<div class="spinner"></div>' +
        '<div id="loading-msg" style="margin-top:16px;color:#fff;font-size:14px;"></div>' +
        '<div id="loading-bar-wrap"><div id="loading-bar-fill"></div></div>' +
        '<div id="loading-pct"></div>' +
      '</div>';
    document.body.appendChild(overlay);
  }
  document.getElementById('loading-msg').textContent = msg || __('common.loading');
  if (typeof percent === 'number') {
    var p = Math.min(100, Math.max(0, percent));
    document.getElementById('loading-bar-wrap').style.display = 'block';
    document.getElementById('loading-bar-fill').style.width = p + '%';
    document.getElementById('loading-pct').style.display = 'block';
    document.getElementById('loading-pct').textContent = Math.round(p) + '%';
  } else {
    document.getElementById('loading-bar-wrap').style.display = 'none';
    document.getElementById('loading-pct').style.display = 'none';
  }
  overlay.style.display = 'flex';
}

function hideLoading() {
  var overlay = document.getElementById('loading-overlay');
  if (overlay) overlay.style.display = 'none';
}

function showResult(msg, type) {
  var el = document.getElementById('result') || document.getElementById('result-upload');
  if (!el) return;
  el.className = type;
  el.innerHTML = msg;
  setTimeout(function() { el.className = ''; el.innerHTML = ''; }, 6000);
}

function esc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

function getConfBadge(filename) {
  for (var i = 0; i < _confidenceScores.length; i++) {
    if (_confidenceScores[i].file === filename || _confidenceScores[i].file === filename.replace('.md','')) {
      var score = _confidenceScores[i].score;
      var color = score >= 0.7 ? '#4ade80' : score >= 0.5 ? '#fbbf24' : '#f87171';
      return '<span class="conf-badge" style="background:' + color + '">' + Math.round(score * 100) + '</span>';
    }
  }
  return '';
}

// ── Delete pending file ──
async function deletePending(filename) {
  if (!confirm(__('delete.confirm') + '「' + filename + '」?')) return;
  showLoading(__('delete.deleting'));
  try {
    const resp = await fetch('/api/kb/pending/delete', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({filename: filename})
    });
    const d = await resp.json();
    hideLoading();
    if (d.ok) {
      showResult(__('delete.success') + filename, 'success');
      refreshPending();
    } else {
      showResult(__('delete.fail') + ': ' + (d.error || '???'), 'error');
    }
  } catch (e) {
    hideLoading();
    showResult(__('delete.fail') + ': ' + e.message, 'error');
  }
}

// ── Search (semantic + RAG) ──
let _searchMode = 'search';
let _searchGroupMode = 'type';
let _lastSearchData = null;
function setSearchMode(mode) {
  _searchMode = mode;
  ['mode-search','mode-ask'].forEach(function(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.toggle('active', (mode === 'search' && id === 'mode-search') || (mode === 'ask' && id === 'mode-ask'));
  });
}

function _getTypeIcon(t) {
  if (t === 'article') return '📄';
  if (t === 'session') return '💬';
  return '📝';
}
function _getTypeLabel(t) {
  if (t === 'article') return __('search.type_article');
  if (t === 'session') return __('search.type_session');
  return __('search.type_note');
}
function _renderSearchResults(data) {
  if (!data || !data.results || !data.results.length) return '';

  // Filter by type checkboxes
  var activeTypes = {};
  document.querySelectorAll('#type-filter-row input[type="checkbox"]').forEach(function(cb) {
    if (cb.checked) activeTypes[cb.value] = true;
  });
  var filtered = data.results.filter(function(r) {
    var t = r.type || 'note';
    return activeTypes[t];
  });
  if (filtered.length === 0) return '';

  var html = '';
  var mode = _searchGroupMode || 'type';

  if (mode === 'type') {
    // Group by type
    var order = [
      { key: 'article', label: '📄 ' + __('search.type_article') },
      { key: 'session', label: '💬 ' + __('search.type_session') },
      { key: 'note', label: '📝 ' + __('search.type_note') }
    ];
    var groups = {};
    filtered.forEach(function(r) {
      var t = r.type || 'note';
      if (!groups[t]) groups[t] = [];
      groups[t].push(r);
    });
    for (var g = 0; g < order.length; g++) {
      var items = groups[order[g].key];
      if (!items || !items.length) continue;
      html += '<div class="search-group">';
      html += '<div class="search-group-title">' + order[g].label + ' (' + items.length + ')</div>';
      html += '<div class="search-results-container">';
      for (var i = 0; i < items.length; i++) {
        html += _renderResultItem(items[i]);
      }
      html += '</div></div>';
    }
  } else {
    // Group by confidence
    var high = [], medium = [], low = [];
    filtered.forEach(function(r) {
      var s = r.confidence ? r.confidence.score : 0;
      if (s >= 0.7) high.push(r);
      else if (s >= 0.5) medium.push(r);
      else low.push(r);
    });
    var confGroups = [
      { items: high, label: __('search.group_high'), icon: '🟢' },
      { items: medium, label: __('search.group_medium'), icon: '🟡' },
      { items: low, label: __('search.group_low'), icon: '🔴' }
    ];
    for (var g = 0; g < confGroups.length; g++) {
      var items = confGroups[g].items;
      if (!items || !items.length) continue;
      html += '<div class="search-group">';
      html += '<div class="search-group-title">' + confGroups[g].icon + ' ' + confGroups[g].label + ' (' + items.length + ')</div>';
      html += '<div class="search-results-container">';
      for (var i = 0; i < items.length; i++) {
        html += _renderResultItem(items[i]);
      }
      html += '</div></div>';
    }
  }
  return html;
}

function _renderResultItem(r) {
  var confScore = r.confidence ? r.confidence.score : 0;
  var badgeColor = confScore >= 0.7 ? '#4ade80' : confScore >= 0.5 ? '#fbbf24' : '#f87171';
  var scoreDisplay = r.score ? 'score: ' + r.score.toFixed(4) : '';
  var typeIcon = _getTypeIcon(r.type || 'note');

  var html = '<div class="search-result-item" style="flex-wrap:wrap;">';
  html += '<div style="display:flex;align-items:center;gap:8px;width:100%;">';
  html += '<span class="confidence-badge" style="background:' + badgeColor + '">' + Math.round(confScore * 100) + '%</span>';
  html += '<span style="margin-right:2px;">' + typeIcon + '</span>';
  html += '<span class="result-title">[[' + esc(r.title) + ']]</span>';
  if (scoreDisplay) html += '<span class="result-score">' + scoreDisplay + '</span>';
  html += '</div>';
  if (r.summary) {
    html += '<div class="result-summary" style="width:100%;">' + esc(r.summary) + '</div>';
  }
  html += '</div>';
  return html;
}

async function doSearch() {
  const q = document.getElementById('search-input').value.trim();
  if (!q) return;
  const resultEl = document.getElementById('search-result');
  showLoading(__('search.searching'));
  try {
    var minConf = document.getElementById('confidence-filter') ? document.getElementById('confidence-filter').value : '0';
    const resp = await fetch('/api/kb/' + (_searchMode === 'ask' ? 'ask' : 'search') + '?q=' + encodeURIComponent(q) + '&min_confidence=' + minConf);
    const data = await resp.json();
    hideLoading();
    if (data.error) {
      resultEl.innerHTML = '<div style="color:#e8963e;padding:12px;">❌ ' + esc(data.error) + '</div>';
      return;
    }
    // Store data for re-filtering
    _lastSearchData = data;

    var html = _renderSearchResults(data);

    // Also show legacy text output
    var output = data.raw_output || data.output || '';
    if (output) {
      html += '<div style="white-space:pre-wrap;font-size:13px;line-height:1.7;color:rgba(255,255,255,0.85);margin-top:12px;border-top:1px solid rgba(255,255,255,0.06);padding-top:12px;">' + esc(output) + '</div>';
    }
    if (!html) {
      html = '<div style="padding:12px;color:rgba(255,255,255,0.4);">' + __('search.no_result') + '</div>';
    }
    resultEl.innerHTML = '<div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:16px;border:1px solid rgba(255,255,255,0.06);"><div style="font-weight:600;color:#d4af37;margin-bottom:10px;font-size:14px;">' + (_searchMode === 'ask' ? __('search.ask_result') : __('search.semantic_result')) + '</div>' + html + '</div>';
  } catch (e) {
    hideLoading();
    resultEl.innerHTML = '<div style="color:#e8963e;padding:12px;">' + __('search.api_error') + esc(e.message) + '</div>';
  }
}

// ── Nebula (Canvas 2D) ──
let _nebulaCtx = null, _nebulaCanvas = null;
let _nebulaNodes = [], _nebulaNodeMap = {}, _nebulaEdges = [];
let _nebulaRotation = 0, _nebulaAnimId = null;
let _viewX = 0, _viewY = 0, _viewScale = 1;
let _hoveredNode = null, _lastMX = 0, _lastMY = 0;
let _nebulaFullMap = {}, _nebulaFullEdges = [];
let _lang = localStorage.getItem('taichu_lang') || 'zh';
const _langPack = {
  zh: {
    // Nav
    'nav.home': '🌌 知识宇宙',
    'nav.upload': '📤 上传',
    'nav.entries': '📄 词条',
    'nav.semantic': '🔍 语义搜索',
    'nav.settings': '⚙ 设置',
    // Common
    'common.online': '在线',
    'common.offline': '离线',
    'common.loading': '加载中...',
    'common.no_data': '无数据',
    'common.save': '保存',
    'common.cancel': '取消',
    'common.confirm': '确认',
    // WS
    'ws.online': '● 在线',
    'ws.offline': '● 离线',
    // Stats
    'stats.total': '总计',
    'stats.wiki': 'Wiki 词条',
    'stats.archive': '归档',
    'stats.wiki_articles': '个 Wiki 词条',
    'stats.core': '核心',
    'stats.archived': '归档',
    // Upload
    'upload.title': '上传文件',
    'upload.drop': '拖放文件到此处，或点击选择',
    'upload.hint': '.md → 直接发布 · 其他格式 → raw/ + 编译',
    'upload.pending': '待编译文件',
    'upload.compile_all': '⚡ 编译全部',
    'upload.empty': '✦ 没有待处理文件',
    'upload.api_unavailable': 'API 不可用',
    'upload.support_error': '不支持的文件类型',
    'upload.success_md': '个 .md 已发布',
    'upload.success_other': '个文件待编译',
    'upload.success': '上传成功',
    'upload.fail': '上传失败',
    'upload.read_fail': '文件读取失败',
    'upload.req_fail': '上传请求失败',
    'upload.path_fail': '无法上传文件路径',
    'upload.compile_loading': '⚡ 编译中，请稍候...（可能需要 1-2 分钟）',
    'upload.complete': '完成',
    'upload.failed': '失败',
    'upload.compile_done': '编译完成',
    'upload.compile_fail': '编译失败',
    'upload.compile_error': '编译 API 错误',
    'upload.uploading': '上传中',
    'upload.error': '上传出错',
    'upload.pending_unit': '个文件待编译',
    // Entries
    'entries.title': '词条',
    'entries.count': '共',
    'entries.page_total': '页',
    'entries.page': '第',
    'entries.prev': '← 上一页',
    'entries.next': '下一页 →',
    'entries.no_match': '无匹配词条',
    'entries.load_fail': '无法加载词条列表',
    'entries.search_placeholder': '搜索词条...',
    // Search
    'search.title': '🔍 语义搜索',
    'search.placeholder': '输入搜索词或问题...',
    'search.semantic': '语义检索',
    'search.ask': 'AI 问答',
    'search.btn': '搜索',
    'search.running': '搜索中...',
    'search.no_query': '请输入搜索词或问题',
    'search.api_error': '搜索 API 不可用',
    'search.semantic_result': '🔎 语义检索结果',
    'search.ask_result': '💬 AI 回答',
    'search.no_result': '无匹配结果',
    'search.searching': '🔍 搜索中...',
    'search.min_confidence': '最低置信度',
    'search.confidence_any': '全部',
    'search.group_type': '按类型',
    'search.group_confidence': '按置信度',
    'search.filter_type': '类型过滤',
    'search.type_article': '文章',
    'search.type_session': '会话',
    'search.type_note': '笔记',
    'search.group_high': '高置信度',
    'search.group_medium': '中等置信度',
    'search.group_low': '较低置信度',
    'search.summary': '摘要',
    'confidence.score': '置信度',
    // Settings nav
    'settings.title': '设置',
    'settings.knowledge': '知识库',
    'settings.database': '数据库',
    'settings.model': '模型',
    'settings.language': '语言',
    'settings.stats': '统计',
    'settings.connection': '连接',
    'settings.runtime': '指标',
    'settings.graphics': '渲染',
    // Settings panels
    'settings.kb_path': '知识库路径',
    'settings.store_path': '存储路径',
    'settings.api_service': 'API 服务',
    'settings.search_engine': '搜索引擎',
    'settings.db_index': '数据库索引',
    'settings.chroma_status': 'ChromaDB',
    'settings.vector_count': '向量索引数',
    'settings.index_collections': '索引集合',
    'settings.ai_model': 'AI 模型',
    'settings.lang_title': '语言',
    'settings.ui_lang': '界面语言',
    'settings.file_stats': '文件统计',
    'settings.conn_status': '连接状态',
    'settings.api_conn': 'API 服务',
    'settings.ws_conn': 'WebSocket',
    'settings.runtime_metrics': '运行指标',
    'settings.render_quality': '渲染画质',
    // Model panel
    'model.current': '当前模型',
    'model.switch': '切换模型',
    'model.select_provider': '— 选择提供商 —',
    'model.switch_to': '切换到',
    'model.base_url': 'Base URL',
    'model.api_endpoint': 'API 入口',
    'model.api_key': 'API Key（留空使用当前）',
    'model.confirm_switch': '确认切换',
    'model.cancel': '取消',
    'model.switching': '⏳ 切换中...',
    'model.no_provider': '请选择提供商',
    'model.req_fail': '请求失败',
    'model.unavailable': '模型信息不可用',
    'model.network_error': '❌ 网络错误',
    'model.role_compile': '编译/推理',
    'model.role_query': '快速问答',
    'model.role_reasoning': '复杂推理',
    'model.role_embedding': '向量嵌入',
    'model.role_vision': '视觉分析',
    'model.switch_title': '切换模型',
    'model.switching_to': '切换到 ',
    // Pipeline trace
    'pipeline.run': '🔍 运行 Pipeline',
    'pipeline.running': '⏳ 运行中...',
    'pipeline.query_parser': '解析查询',
    'pipeline.vector_search': '向量搜索',
    'pipeline.graph_expand': '图谱扩展',
    'pipeline.ontology_filter': '本体过滤',
    'pipeline.rerank': '重排序',
    'pipeline.context_builder': '上下文组装',
    'pipeline.total': '总计',
    'pipeline.results': '结果数',
    'pipeline.graph_expanded': '图谱扩展',
    'pipeline.nodes': '节点',
    'pipeline.reference': '参考：<span style="color:#4ade80;">✓ &lt;200ms</span> · <span style="color:#fbbf24;">⚠ 200~1000ms</span> · <span style="color:#f87171;">✗ &gt;1s</span>',
    // Metrics
    'metrics.retrieval_count': '检索次数',
    'metrics.avg_latency': '平均耗时',
    'metrics.graph_nodes': '图谱节点',
    'metrics.orphan_nodes': '孤岛节点',
    'metrics.avg_neighbors': '平均邻居',
    'metrics.unavailable': '指标不可用',
    'metrics.load_fail': '指标加载失败',
    'metrics.eventbus': 'EventBus',
    // GFX
    'gfx.renderer': '渲染引擎',
    'gfx.view_mode': '视图模式',
    'gfx.layout_mode': '布局模式',
    'gfx.node_limit': '节点上限',
    'gfx.rotation_speed': '旋转速度',
    'gfx.node_size': '节点大小',
    'gfx.cpu': 'CPU (2D Canvas)',
    'gfx.gpu': 'GPU (WebGL)',
    'gfx._2d': '2D',
    'gfx._3d': '3D',
    'gfx.spiral': '螺旋星系',
    'gfx.neural': '神经网络',
    'gfx.off': '关闭',
    'gfx.slow': '0.5x',
    'gfx.normal': '1x',
    'gfx.fast': '2x',
    'gfx.small': '小',
    'gfx.medium': '中',
    'gfx.large': '大',
    'gfx.hint_renderer': 'GPU 使用硬件加速，适合大量节点',
    'gfx.hint_view': '3D 仅 GPU 模式可用',
    'gfx.hint_limit': '数量越大性能开销越大',
    'gfx.updated': '✔ 已更新',
    'gfx.webgl_unavailable': '⚠ 当前环境不支持 WebGL',
    // GFX old keys (keep for compat)
    'gfx.layout_spiral': '螺旋星系',
    'gfx.layout_force': '力导向',
    'gfx.speed_off': '关闭',
    'gfx.3d_warn': '⚠ 3D 模式需要切换到 GPU (WebGL) 渲染引擎',
    // Panel / Nebula
    'panel.title': '知识节点',
    'panel.title_en': 'Node Insight',
    'panel.placeholder': '悬停节点查看详情',
    'panel.cluster': '集群',
    'panel.gravity': '重力',
    'panel.neighbors': '关联节点',
    'panel.not_found': '未找到节点',
    'panel.no_label': '悬停或点击节点查看详情',
    // Nebula
    'nebula.loading': '加载星云数据...',
    'nebula.search_placeholder': '输入节点名称跳转...',
    'nebula.search_placeholder2': '输入节点名称...',
    'nebula.goto': '跳转',
    'nebula.hint': '滚轮缩放 · 双击聚焦',
    'nebula.mode_3d': '3D 全息模式',
    'nebula.empty': '✦ 暂无词条',
    // Delete
    'delete.confirm': '确定删除',
    'delete.success': '已删除',
    'delete.fail': '删除失败',
    'delete.deleting': '正在删除...',
    // Result toast
    'result.update': '已更新',
    // Misc
    'gpu.fallback': '⚠ Three.js 加载失败，回退到 CPU 模式',
    'settings.chroma_online': '● 运行中',
    'settings.chroma_offline': '● 不可用',
    'settings.api_down': 'API 不可用',
    'compile.none': '没有待编译的文件',
    'compile.done': '✔ 编译完成，共',
    // Nav (new)
    'nav.memory': '🧠 Agent 记忆',
    'nav.aging': '📊 老化列表',
    // Memory dashboard
    'memory.title': '🧠 Agent 记忆管理',
    'memory.agent_count': '接入 Agent',
    'memory.total': '记忆总条数',
    'memory.sessions': '会话数',
    'memory.agent_dist': 'Agent 分布',
    'memory.type_dist': '记忆类型分布',
    'memory.recent': '最近会话',
    'memory.detail': 'Agent 详情',
    'memory.table_agent': 'Agent',
    'memory.table_memories': '记忆条数',
    'memory.table_sessions': '会话数',
    'memory.table_types': '类型',
    'memory.table_last': '最后活跃',
    'memory.loading': '加载中...',
    'memory.no_data': '暂无数据',
    // Aging dashboard
    'aging.title': '📊 知识老化列表',
    'aging.scanned': '已扫描',
    'aging.notice': '注意',
    'aging.aging_label': '老化',
    'aging.stale': '陈旧',
    'aging.distribution': '老化等级分布',
    'aging.batch_mark': '🏷 批量标记 aging',
    'aging.archive': '📦 建议归档',
    'aging.ranking': '老化排行榜',
    'aging.table_file': '文件',
    'aging.table_score': '分数',
    'aging.table_tier': '等级',
    'aging.table_time': '时间衰减',
    'aging.table_freq': '频率',
    'aging.table_confidence': '置信度',
    'aging.updated': '上次更新: ',
    'aging.load_fail': '加载失败: ',
    'compile.files': '个',
  },
  en: {
    'nav.home': '🌌 Universe',
    'nav.upload': '📤 Upload',
    'nav.entries': '📄 Entries',
    'nav.semantic': '🔍 Search',
    'nav.settings': '⚙ Settings',
    'common.online': 'Online',
    'common.offline': 'Offline',
    'common.loading': 'Loading...',
    'common.no_data': 'No data',
    'common.save': 'Save',
    'common.cancel': 'Cancel',
    'common.confirm': 'Confirm',
    'ws.online': '● Online',
    'ws.offline': '● Offline',
    'stats.total': 'Total',
    'stats.wiki': 'Wiki Articles',
    'stats.archive': 'Archived',
    'stats.wiki_articles': 'Wiki Articles',
    'stats.core': 'Core',
    'stats.archived': 'Archived',
    'upload.title': 'Upload Files',
    'upload.drop': 'Drop files here, or click to select',
    'upload.hint': '.md → Direct publish · Other → raw/ + compile',
    'upload.pending': 'Pending Files',
    'upload.compile_all': 'Compile All',
    'upload.empty': '✦ No pending files',
    'upload.api_unavailable': 'API unavailable',
    'upload.support_error': 'Unsupported file type',
    'upload.success_md': ' .md published',
    'upload.success_other': ' files pending',
    'upload.success': 'Upload successful',
    'upload.fail': 'Upload failed',
    'upload.read_fail': 'File read failed',
    'upload.req_fail': 'Upload request failed',
    'upload.path_fail': 'Cannot upload file path',
    'upload.compile_loading': 'Compiling, please wait... (1-2 min)',
    'upload.complete': 'Complete',
    'upload.failed': 'Failed',
    'upload.compile_done': 'Compile complete',
    'upload.compile_fail': 'Compile failed',
    'upload.compile_error': 'Compile API error',
    'upload.uploading': 'Uploading',
    'upload.error': 'Upload error',
    'upload.pending_unit': 'files pending',
    'entries.title': 'Entries',
    'entries.count': 'Total',
    'entries.page_total': 'pages',
    'entries.page': 'Page',
    'entries.prev': '← Prev',
    'entries.next': 'Next →',
    'entries.no_match': 'No matching entries',
    'entries.load_fail': 'Cannot load entries',
    'entries.search_placeholder': 'Search entries...',
    'search.title': '🔍 Semantic Search',
    'search.placeholder': 'Enter search term or question...',
    'search.semantic': 'Semantic',
    'search.ask': 'AI Q&A',
    'search.btn': 'Search',
    'search.running': 'Searching...',
    'search.no_query': 'Please enter a search term',
    'search.api_error': 'Search API unavailable',
    'search.semantic_result': '🔎 Semantic Results',
    'search.ask_result': '💬 AI Answer',
    'search.no_result': 'No matching results',
    'search.searching': '🔍 Searching...',
    'search.min_confidence': 'Min Confidence',
    'search.confidence_any': 'All',
    'search.group_type': 'By Type',
    'search.group_confidence': 'By Confidence',
    'search.filter_type': 'Type Filter',
    'search.type_article': 'Articles',
    'search.type_session': 'Sessions',
    'search.type_note': 'Notes',
    'search.group_high': 'High Confidence',
    'search.group_medium': 'Medium',
    'search.group_low': 'Low',
    'search.summary': 'Summary',
    'confidence.score': 'Confidence',
    'settings.title': 'Settings',
    'settings.knowledge': 'Knowledge',
    'settings.database': 'Database',
    'settings.model': 'Model',
    'settings.language': 'Language',
    'settings.stats': 'Stats',
    'settings.connection': 'Connection',
    'settings.runtime': 'Runtime',
    'settings.graphics': 'Graphics',
    'settings.kb_path': 'Knowledge Base Path',
    'settings.store_path': 'Storage Path',
    'settings.api_service': 'API Service',
    'settings.search_engine': 'Search Engine',
    'settings.db_index': 'Database Index',
    'settings.chroma_status': 'ChromaDB',
    'settings.vector_count': 'Vector Count',
    'settings.index_collections': 'Collections',
    'settings.ai_model': 'AI Model',
    'settings.lang_title': 'Language',
    'settings.ui_lang': 'Interface Language',
    'settings.file_stats': 'File Statistics',
    'settings.conn_status': 'Connection Status',
    'settings.api_conn': 'API Service',
    'settings.ws_conn': 'WebSocket',
    'settings.runtime_metrics': 'Runtime Metrics',
    'settings.render_quality': 'Render Quality',
    'model.current': 'Current Model',
    'model.switch': 'Switch Model',
    'model.select_provider': '— Select Provider —',
    'model.switch_to': 'Switch to',
    'model.base_url': 'Base URL',
    'model.api_endpoint': 'API Endpoint',
    'model.api_key': 'API Key (leave empty)',
    'model.confirm_switch': 'Confirm',
    'model.cancel': 'Cancel',
    'model.switching': '⏳ Switching...',
    'model.no_provider': 'Select a provider',
    'model.req_fail': 'Request failed',
    'model.unavailable': 'Model info unavailable',
    'model.network_error': '❌ Network error',
    'model.role_compile': 'Compile/Reason',
    'model.role_query': 'Quick Q&A',
    'model.role_reasoning': 'Deep Reasoning',
    'model.role_embedding': 'Embedding',
    'model.role_vision': 'Vision',
    'model.switch_title': 'Switch Model',
    'model.switching_to': 'Switch to ',
    'pipeline.run': 'Run Pipeline',
    'pipeline.running': 'Running...',
    'pipeline.query_parser': 'Query Parser',
    'pipeline.vector_search': 'Vector Search',
    'pipeline.graph_expand': 'Graph Expand',
    'pipeline.ontology_filter': 'Ontology Filter',
    'pipeline.rerank': 'Re-rank',
    'pipeline.context_builder': 'Context Builder',
    'pipeline.total': 'Total',
    'pipeline.results': 'Results',
    'pipeline.graph_expanded': 'Graph Expanded',
    'pipeline.nodes': 'nodes',
    'pipeline.reference': 'Reference: <span style="color:#4ade80;">✓ &lt;200ms</span> · <span style="color:#fbbf24;">⚠ 200~1000ms</span> · <span style="color:#f87171;">✗ &gt;1s</span>',
    'metrics.retrieval_count': 'Retrieval Count',
    'metrics.avg_latency': 'Avg Latency',
    'metrics.graph_nodes': 'Graph Nodes',
    'metrics.orphan_nodes': 'Orphan Nodes',
    'metrics.avg_neighbors': 'Avg Neighbors',
    'metrics.unavailable': 'Metrics unavailable',
    'metrics.load_fail': 'Metrics load failed',
    'metrics.eventbus': 'EventBus',
    'gfx.renderer': 'Renderer',
    'gfx.view_mode': 'View Mode',
    'gfx.layout_mode': 'Layout Mode',
    'gfx.node_limit': 'Node Limit',
    'gfx.rotation_speed': 'Rotation Speed',
    'gfx.node_size': 'Node Size',
    'gfx.cpu': 'CPU (2D Canvas)',
    'gfx.gpu': 'GPU (WebGL)',
    'gfx._2d': '2D',
    'gfx._3d': '3D',
    'gfx.spiral': 'Spiral Galaxy',
    'gfx.neural': 'Neural Network',
    'gfx.off': 'Off',
    'gfx.slow': '0.5x',
    'gfx.normal': '1x',
    'gfx.fast': '2x',
    'gfx.small': 'Small',
    'gfx.medium': 'Medium',
    'gfx.large': 'Large',
    'gfx.hint_renderer': 'GPU uses hardware acceleration, best for large graphs',
    'gfx.hint_view': '3D requires GPU mode',
    'gfx.hint_limit': 'Higher values use more resources',
    'gfx.updated': '✔ Updated',
    'gfx.webgl_unavailable': '⚠ WebGL not available',
    'gfx.layout_spiral': 'Spiral',
    'gfx.layout_force': 'Force',
    'gfx.speed_off': 'Off',
    'gfx.3d_warn': '⚠ 3D requires GPU (WebGL) renderer',
    'panel.title': '知识节点',
    'panel.title_en': 'Node Insight',
    'panel.placeholder': 'Hover over a node for details',
    'panel.cluster': 'Cluster',
    'panel.gravity': 'Gravity',
    'panel.neighbors': 'Neighbors',
    'panel.not_found': 'Node not found',
    'panel.no_label': 'Hover or click a node for details',
    'nebula.loading': 'Loading nebula data...',
    'nebula.search_placeholder': 'Jump to node...',
    'nebula.search_placeholder2': 'Enter node name...',
    'nebula.goto': 'Go',
    'nebula.hint': 'Scroll to zoom · Double-click to focus',
    'nebula.mode_3d': '3D Hologram',
    'nebula.empty': '✦ No entries',
    'delete.confirm': 'Confirm delete',
    'delete.success': 'Deleted',
    'delete.fail': 'Delete failed',
    'delete.deleting': 'Deleting...',
    'result.update': 'Updated',
    'gpu.fallback': '⚠ Three.js failed, fallback to CPU',
    'settings.chroma_online': '● Online',
    'settings.chroma_offline': '● Unavailable',
    'settings.api_down': 'API unavailable',
    'compile.none': 'No files to compile',
    // Nav (new)
    'nav.memory': '🧠 Memory',
    'nav.aging': '📊 Aging',
    // Memory dashboard
    'memory.title': '🧠 Agent Memory',
    'memory.agent_count': 'Agents',
    'memory.total': 'Total Memories',
    'memory.sessions': 'Sessions',
    'memory.agent_dist': 'Agent Distribution',
    'memory.type_dist': 'Memory Type Distribution',
    'memory.recent': 'Recent Sessions',
    'memory.detail': 'Agent Details',
    'memory.table_agent': 'Agent',
    'memory.table_memories': 'Memories',
    'memory.table_sessions': 'Sessions',
    'memory.table_types': 'Types',
    'memory.table_last': 'Last Active',
    'memory.loading': 'Loading...',
    'memory.no_data': 'No Data',
    // Aging dashboard
    'aging.title': '📊 Knowledge Aging',
    'aging.scanned': 'Scanned',
    'aging.notice': 'Notice',
    'aging.aging_label': 'Aging',
    'aging.stale': 'Stale',
    'aging.distribution': 'Aging Distribution',
    'aging.batch_mark': '🏷 Batch Mark Aging',
    'aging.archive': '📦 Archive Suggestions',
    'aging.ranking': 'Aging Rankings',
    'aging.table_file': 'File',
    'aging.table_score': 'Score',
    'aging.table_tier': 'Tier',
    'aging.table_time': 'Time Decay',
    'aging.table_freq': 'Frequency',
    'aging.table_confidence': 'Confidence',
    'aging.updated': 'Last Updated: ',
    'aging.load_fail': 'Load Failed: ',
    'compile.files': '',
  },
};
function __(k) { return (_langPack[_lang] || _langPack.zh)[k] || k; }
let _gfxSettings = {};
let _gfxNodeLimit = 150;
let _gfxRotationSpeed = 1;
let _gfxNodeSizeScale = 1;

function _screenToWorld(sx, sy) {
  return { x: (sx - _viewX) / _viewScale, y: (sy - _viewY) / _viewScale };
}

function _galaxyLayout(data, opts) {
  opts = opts || {};
  var mode = opts.layout || 'spiral';
  var sizeScale = opts.sizeScale || 1;
  var nodes = [], map = {};
  var cx = 0, cy = 0;
  var center = { id:'\u592a\u521d', label:'\u592a\u521d', x:cx, y:cy, galR:0, galAngle:0, size:20, summary:'\u592a\u521d\u77e5\u8bc6\u5b87\u5b99\u6838\u5fc3', links:[] };
  nodes.push(center); map['\u592a\u521d'] = center;
  var others = data.nodes.filter(function(n) { return n.id !== '\u592a\u521d'; });
  // Neural cluster centers (for circle mode)
  var clusterCenters = null;
  if (mode === 'circle') {
    clusterCenters = [];
    for (var ci = 0; ci < 4; ci++) {
      var ca = (ci / 4) * Math.PI * 2 + 0.3;
      var cr = 100 + Math.random() * 150;
      clusterCenters.push({ x: Math.cos(ca) * cr, y: Math.sin(ca) * cr * 0.6, spread: 50 + Math.random() * 70 });
    }
  }
  for (var i = 0; i < others.length; i++) {
    var n = others[i];
    if (mode === 'circle') {
      var cc = clusterCenters[i % 4];
      var a = Math.random() * Math.PI * 2;
      var r = Math.random() * cc.spread;
      var x = cc.x + Math.cos(a) * r;
      var y = cc.y + Math.sin(a) * r;
      nodes.push({
        id: n.id, label: n.label, x: x, y: y,
        galR: Math.sqrt(x * x + y * y),
        galAngle: Math.atan2(y, x),
        size: Math.max(4, Math.min(14, (n.value || 1) * 2.5 * sizeScale)),
        summary: n.summary || '', links: n.links || []
      });
    } else {
      var angle = i * 3.5;
      var radius = 80 + Math.random() * 380;
      nodes.push({
        id: n.id, label: n.label,
        x: cx + Math.cos(angle) * radius, y: cy + Math.sin(angle) * radius,
        galR: radius, galAngle: angle,
        size: Math.max(4, Math.min(14, (n.value || 1) * 2.5 * sizeScale)),
        summary: n.summary || '', links: n.links || []
      });
    }
    map[n.id] = nodes[nodes.length - 1];
  }
  return { nodes: nodes, map: map, edges: data.edges || [] };
}

function _showTooltip(nodeId) {
  var el = document.getElementById('panel-content');
  if (!el) return;
  if (!nodeId || !_nebulaNodeMap[nodeId]) { el.innerHTML = __('panel.no_label'); return; }
  var n = _nebulaNodeMap[nodeId];
  var linksText = (n.links || []).slice(0, 8).join(' \xb7 ') || __('common.no_data');
  el.innerHTML = '<div style="font-weight:600;color:#d4af37;margin-bottom:4px;">\ud83d\udcc4 ' + n.label + '</div><div style="font-size:0.85em;color:#ccc;margin-bottom:6px;line-height:1.4;">' + (n.summary || '(' + __('common.no_data') + ')') + '</div><div style="font-size:0.75em;color:#888;">\ud83d\udd17 ' + linksText + '</div>';
}

function updateLangUI(){
  // Update panel title
  var el=document.getElementById('panel-title');
  if(el){el.textContent=_lang==='en'?'Node Insight':'\u77e5\u8bc6\u8282\u70b9';}
  // Update all data-i18n elements
  document.querySelectorAll('[data-i18n]').forEach(function(el){
    var key=el.dataset.i18n;
    el.textContent=__(key);
  });
  // Update data-i18n-placeholder elements
  document.querySelectorAll('[data-i18n-placeholder]').forEach(function(el){
    el.placeholder=__(el.dataset.i18nPlaceholder);
  });
}

function _renderLoop() {
  var ctx = _nebulaCtx, cvs = _nebulaCanvas;
  if (!ctx || !cvs) return;
  var parent = cvs.parentElement;
  if (parent && (cvs.width !== parent.clientWidth || cvs.height !== parent.clientHeight)) {
    cvs.width = parent.clientWidth; cvs.height = parent.clientHeight;
  }
  var w = cvs.width, h = cvs.height;
  var homeTab = document.getElementById('tab-home');
  if (!homeTab || homeTab.style.display === 'none') {
    _nebulaAnimId = requestAnimationFrame(_renderLoop);
    return;
  }
  if(_gfxSettings.layout_mode!=='circle')_nebulaRotation+=0.003*_gfxRotationSpeed;
  var cx = w / 2, cy = h / 2;
  var cosR = Math.cos(_nebulaRotation), sinR = Math.sin(_nebulaRotation);
  for (var i = 0; i < _nebulaNodes.length; i++) {
    var n = _nebulaNodes[i];
    if (n.id === '\u592a\u521d') { n.x = cx; n.y = cy; }
    else { n.x = cx + cosR * n.galR * Math.cos(n.galAngle) - sinR * n.galR * Math.sin(n.galAngle);
           n.y = cy + sinR * n.galR * Math.cos(n.galAngle) + cosR * n.galR * Math.sin(n.galAngle); }
  }
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, w, h);
  ctx.save(); ctx.translate(_viewX, _viewY); ctx.scale(_viewScale, _viewScale);
  // Edges
  var edgeAlpha = (_gfxSettings && _gfxSettings.layout_mode === 'circle') ? '0.4' : '0.2';
  ctx.strokeStyle = 'rgba(100,180,255,' + edgeAlpha + ')'; ctx.lineWidth = 0.5 / _viewScale;
  for (var i = 0; i < _nebulaEdges.length; i++) {
    var e = _nebulaEdges[i];
    var f = _nebulaNodeMap[e.from], t = _nebulaNodeMap[e.to];
    if (f && t) { ctx.beginPath(); ctx.moveTo(f.x, f.y); ctx.lineTo(t.x, t.y); ctx.stroke(); }
  }
  // Hover detection
  var world = _screenToWorld(_lastMX, _lastMY);
  var hoverId = null;
  for (var i = 0; i < _nebulaNodes.length; i++) {
    var n = _nebulaNodes[i];
    var ns = n.id === '\u592a\u521d' ? 20 : n.size;
    var dx = n.x - world.x, dy = n.y - world.y;
    if (dx * dx + dy * dy < (ns + 5) * (ns + 5)) hoverId = n.id;
  }
  if (hoverId !== _hoveredNode) { _hoveredNode = hoverId; _showTooltip(hoverId, _lastMX, _lastMY); }
  // 太初节点置底：柔和光晕 + 小核心，避免蛋黄感
  var _centerNode = _nebulaNodeMap['\u592a\u521d'];
  if (_centerNode) {
    // Outer glow
    ctx.save();
    var _cg = ctx.createRadialGradient(_centerNode.x, _centerNode.y, 0, _centerNode.x, _centerNode.y, 70);
    _cg.addColorStop(0, 'rgba(255,200,100,0.06)');
    _cg.addColorStop(1, 'rgba(255,200,100,0)');
    ctx.fillStyle = _cg;
    ctx.beginPath(); ctx.arc(_centerNode.x, _centerNode.y, 70, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
    // Inner glow
    ctx.save();
    var _cg2 = ctx.createRadialGradient(_centerNode.x, _centerNode.y, 0, _centerNode.x, _centerNode.y, 25);
    _cg2.addColorStop(0, 'rgba(255,220,120,0.10)');
    _cg2.addColorStop(1, 'rgba(255,220,120,0)');
    ctx.fillStyle = _cg2;
    ctx.beginPath(); ctx.arc(_centerNode.x, _centerNode.y, 25, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
    // Small bright core
    ctx.beginPath(); ctx.arc(_centerNode.x, _centerNode.y, 5, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255,220,120,0.7)';
    ctx.fill();
  }

  // Draw other nodes (on top of center)
  for (var i = 0; i < _nebulaNodes.length; i++) {
    var n = _nebulaNodes[i];
    if (n.id === '\u592a\u521d') continue;
    var isHov = n.id === _hoveredNode;
    var ns = n.size;
    var alpha = Math.max(0.35, 0.5);

    // Outer glow for hovered
    if (isHov) {
      ctx.save();
      ctx.beginPath();
      ctx.arc(n.x, n.y, ns * 3, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(100,200,255,0.10)';
      ctx.fill();
      ctx.restore();
    }

    // Radial gradient → 3D sphere
    var grad = ctx.createRadialGradient(
      n.x - ns * 0.3, n.y - ns * 0.4, 0,
      n.x, n.y, ns
    );
    if (isHov) {
      grad.addColorStop(0, '#e0f4ff');
      grad.addColorStop(0.5, '#5bb8f0');
      grad.addColorStop(1, '#1a6bb5');
    } else {
      grad.addColorStop(0, 'rgba(180,220,255,' + (alpha + 0.1) + ')');
      grad.addColorStop(0.6, 'rgba(60,140,255,' + alpha + ')');
      grad.addColorStop(1, 'rgba(30,70,180,' + alpha + ')');
    }

    ctx.beginPath();
    ctx.arc(n.x, n.y, ns, 0, Math.PI * 2);
    ctx.fillStyle = grad;
    ctx.fill();

    // Subtle border
    ctx.strokeStyle = isHov ? 'rgba(180,220,255,0.5)' : 'rgba(100,160,255,0.15)';
    ctx.lineWidth = isHov ? 1 : 0.5;
    ctx.stroke();
  }
  ctx.restore();
  _nebulaAnimId = requestAnimationFrame(_renderLoop);
}

function _initNebulaEvents(graphEl) {
  graphEl.addEventListener('mousemove', function(e) { _lastMX = e.offsetX; _lastMY = e.offsetY; });
  graphEl.addEventListener('wheel', function(e) {
    e.preventDefault();
    var d = e.deltaY > 0 ? 0.9 : 1.1;
    var ns = _viewScale * d;
    if (ns < 0.1 || ns > 5) return;
    _viewX = e.offsetX - (e.offsetX - _viewX) * d;
    _viewY = e.offsetY - (e.offsetY - _viewY) * d;
    _viewScale = ns;
  }, { passive: false });
  graphEl.addEventListener('dblclick', function(e) {
    var w = _screenToWorld(e.offsetX, e.offsetY);
    var best = null, bestD = Infinity;
    for (var i = 0; i < _nebulaNodes.length; i++) {
      var n = _nebulaNodes[i];
      var dx = n.x - w.x, dy = n.y - w.y, d = dx * dx + dy * dy;
      if (d < bestD) { bestD = d; best = n; }
    }
    if (best && bestD < 10000) {
      var ns = 2; _viewX = e.offsetX - best.x * ns; _viewY = e.offsetY - best.y * ns; _viewScale = ns;
      _hoveredNode = best.id; _showTooltip(best.id);
    }
  });
}

async function refreshNebula() {
  var graphEl = document.getElementById('kb-graph');
  if (!graphEl) return;
  if (graphEl.offsetHeight < 100) { graphEl.style.height = (window.innerHeight - 40) + 'px'; }
  if (graphEl.offsetWidth === 0) { requestAnimationFrame(function() { refreshNebula(); }); return; }
  // GPU mode: destroy Canvas if active, build Three.js scene
  if (_gfxSettings.renderer === 'gpu') {
    if (_nebulaAnimId) { cancelAnimationFrame(_nebulaAnimId); _nebulaAnimId = null; }
    _nebulaCanvas = null; _nebulaCtx = null;
    _gfxRefreshNebula(graphEl);
    return;
  }
  // CPU mode: destroy Three.js if active
  _destroyThreeScene();
  // Show loading state
  graphEl.innerHTML = '<div style="color:#666;text-align:center;padding-top:170px;font-size:13px;"><span style="display:inline-block;width:20px;height:20px;border:2px solid #333;border-top-color:#7dd3fc;border-radius:50%;animation:_spin 0.8s linear infinite;margin-bottom:12px;"></span><br>' + __('nebula.loading') + '</div>';
  // Inject spin keyframe once
  if (!document.getElementById('_spin_style')) {
    var s = document.createElement('style'); s.id = '_spin_style';
    s.textContent = '@keyframes _spin{to{transform:rotate(360deg)}}';
    document.head.appendChild(s);
  }
  try {
    var limit = _gfxNodeLimit || 150;
    var resp = await fetch('/api/kb/graph?limit=' + limit);
    var data = await resp.json();
    if (!graphEl) return;
    if (data.error || !data.nodes || data.nodes.length === 0) {
      graphEl.innerHTML = '<div style="color:#888;text-align:center;padding-top:170px;font-size:13px;">' + __('nebula.empty') + '</div>';
      return;
    }
    var layout = _galaxyLayout(data, {
      layout: _gfxSettings.layout_mode || 'spiral',
      sizeScale: _gfxNodeSizeScale || 1
    });
    _nebulaNodes = layout.nodes;
    _nebulaNodeMap = layout.map;
    _nebulaEdges = layout.edges;
    // Create canvas
    if (!_nebulaCanvas || !graphEl.contains(_nebulaCanvas)) {
      graphEl.innerHTML = '';
      var cvs = document.createElement('canvas');
      cvs.style.cssText = 'display:block;width:100%;height:100%;';
      cvs.width = graphEl.clientWidth; cvs.height = graphEl.clientHeight;
      graphEl.appendChild(cvs);
      _nebulaCanvas = cvs;
      _nebulaCtx = cvs.getContext('2d');
      _viewX = 0; _viewY = 0; _viewScale = 1;
      _initNebulaEvents(graphEl);
    }
    // Stop old animation, start new
    _nebulaRotation = 0;
    if (_nebulaAnimId) cancelAnimationFrame(_nebulaAnimId);
    _nebulaAnimId = requestAnimationFrame(_renderLoop);
    // Load full data in background for search
    fetch('/api/kb/graph?limit=9999').then(function(r) { return r.json(); }).then(function(d) {
      if (d.nodes) { _nebulaFullMap = {}; d.nodes.forEach(function(n) { _nebulaFullMap[n.id] = n; }); _nebulaFullEdges = d.edges || []; }
    }).catch(function() {});
  } catch (e) { console.error('Nebula error:', e); }
}

function doNebulaSearch() {
  var input = document.getElementById('nebula-search-input');
  if (!input) return;
  var q = input.value.trim().toLowerCase();
  if (!q) return;
  var matched = _nebulaNodes.filter(function(n) { return n.label && n.label.toLowerCase().indexOf(q) !== -1; });
  if (matched.length > 0) {
    var n = matched[0];
    _viewScale = 2; _viewX = _nebulaCanvas.width / 2 - n.x * 2; _viewY = _nebulaCanvas.height / 2 - n.y * 2;
    _hoveredNode = n.id; _showTooltip(n.id, _lastMX, _lastMY);
    return;
  }
  // Search full data
  if (Object.keys(_nebulaFullMap).length > 0) {
    for (var id in _nebulaFullMap) {
      var label = _nebulaFullMap[id].label || '';
      if (label.toLowerCase().indexOf(q) !== -1) {
        showLoading('\ud83c\udf00 ' + __('common.loading'));
        fetch('/api/kb/graph?expand=' + encodeURIComponent(id)).then(function(r) { return r.json(); }).then(function(data) {
          hideLoading();
          if (data.nodes) {
            var layout = _galaxyLayout(data, {
              layout: _gfxSettings.layout_mode || 'spiral',
              sizeScale: _gfxNodeSizeScale || 1
            });
            _nebulaNodes = layout.nodes;
            _nebulaNodeMap = layout.map;
            _nebulaEdges = layout.edges;
            _nebulaRotation = 0;
          }
        }).catch(function(e) { hideLoading(); });
        return;
      }
    }
  }
}

// ── Three.js GPU Renderer ──
var _threeLoaded = false;
var _threeReady = false;
var _threeScene = null, _threeRenderer = null, _threeCamera = null;
var _threeControls = null, _threeLabelRenderer = null;
var _threePoints = null, _threeCenterSprite = null;
var _threeLines = null, _threeGroup = null;
var _threeAnimId = null;
var _threeNodeData = [];
var _threeHoveredIdx = -1;

function _loadScript(src) {
  return new Promise(function(resolve, reject) {
    if (document.querySelector('script[src="' + src + '"]')) { resolve(); return; }
    var s = document.createElement('script');
    s.onload = resolve; s.onerror = reject;
    s.src = src;
    document.head.appendChild(s);
  });
}

async function _ensureThreeJs() {
  if (_threeLoaded) return true;
  try {
    await _loadScript('https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js');
    await _loadScript('https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js');
    await _loadScript('https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/renderers/CSS2DRenderer.js');
    _threeLoaded = true;
    return true;
  } catch (e) {
    console.error('Three.js load failed:', e);
    return false;
  }
}

function _createGlowTexture(gold) {
  var c = document.createElement('canvas');
  c.width = 64; c.height = 64;
  var ctx = c.getContext('2d');
  var g = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
  if (gold) {
    g.addColorStop(0, 'rgba(255,215,0,1)');
    g.addColorStop(0.3, 'rgba(255,215,0,0.7)');
    g.addColorStop(1, 'rgba(255,215,0,0)');
  } else {
    g.addColorStop(0, 'rgba(180,210,255,1)');
    g.addColorStop(0.3, 'rgba(100,150,255,0.6)');
    g.addColorStop(1, 'rgba(100,150,255,0)');
  }
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 64, 64);
  return new THREE.CanvasTexture(c);
}

function _destroyThreeScene() {
  if (_threeAnimId) { cancelAnimationFrame(_threeAnimId); _threeAnimId = null; }
  _threeReady = false;
  if (_threeControls) { _threeControls.dispose(); _threeControls = null; }
  if (_threeRenderer) {
    _threeRenderer.dispose();
    if (_threeRenderer.domElement && _threeRenderer.domElement.parentNode)
      _threeRenderer.domElement.parentNode.removeChild(_threeRenderer.domElement);
    _threeRenderer = null;
  }
  if (_threeLabelRenderer) {
    if (_threeLabelRenderer.domElement && _threeLabelRenderer.domElement.parentNode)
      _threeLabelRenderer.domElement.parentNode.removeChild(_threeLabelRenderer.domElement);
    _threeLabelRenderer = null;
  }
  if (_threeCenterSprite) {
    _threeCenterSprite.material.dispose();
    _threeCenterSprite = null;
  }
  _threeScene = null; _threeCamera = null;
  _threePoints = null; _threeLines = null; _threeGroup = null;
  _threeNodeData = []; _threeHoveredIdx = -1;
}

function _buildThreeScene(graphEl, data) {
  var is3D = _gfxSettings.view_mode === '3d';
  var sizeScale = _gfxNodeSizeScale || 1;
  var sizeMul = 10 * sizeScale;
  var centerSize = 40 * sizeScale;

  var layout = _galaxyLayout(data, {
    layout: _gfxSettings.layout_mode || 'spiral',
    sizeScale: sizeScale
  });
  _threeNodeData = layout.nodes;

  var scene = new THREE.Scene();
  scene.background = new THREE.Color(0x000000);

  var w = graphEl.clientWidth || 800;
  var h = graphEl.clientHeight || 600;
  var camera = new THREE.PerspectiveCamera(50, w / h, 1, 5000);
  if (is3D) {
    camera.position.set(0, 250, 500);
  } else {
    camera.position.set(0, 0, 900);
  }
  camera.lookAt(0, 0, 0);

  var renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(w, h);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.domElement.style.cssText = 'display:block;width:100%;height:100%;';
  graphEl.innerHTML = '';
  graphEl.appendChild(renderer.domElement);

  var labelRenderer = new THREE.CSS2DRenderer();
  labelRenderer.setSize(w, h);
  labelRenderer.domElement.style.position = 'absolute';
  labelRenderer.domElement.style.top = '0';
  labelRenderer.domElement.style.left = '0';
  labelRenderer.domElement.style.pointerEvents = 'none';
  graphEl.appendChild(labelRenderer.domElement);

  var controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.minDistance = 100;
  controls.maxDistance = 2500;
  if (is3D) {
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.5 * (_gfxRotationSpeed || 1);
    controls.target.set(0, 0, 0);
  } else {
    controls.enableRotate = false;
    controls.mouseButtons = { LEFT: THREE.MOUSE.PAN, MIDDLE: THREE.MOUSE.DOLLY, RIGHT: THREE.MOUSE.PAN };
  }

  var glowTex = _createGlowTexture(false);
  var goldTex = _createGlowTexture(true);
  var group = new THREE.Group();

  // Points for all nodes
  var pos = new Float32Array(layout.nodes.length * 3);
  var col = new Float32Array(layout.nodes.length * 3);
  var centerIdx = -1;
  for (var i = 0; i < layout.nodes.length; i++) {
    var n = layout.nodes[i];
    pos[i * 3] = n.x; pos[i * 3 + 1] = n.y;
    pos[i * 3 + 2] = is3D ? (Math.random() - 0.5) * 80 : 0;
    if (n.id === '太初') {
      col[i * 3] = 1; col[i * 3 + 1] = 0.84; col[i * 3 + 2] = 0.2;
      centerIdx = i;
    } else {
      col[i * 3] = 0.3; col[i * 3 + 1] = 0.55; col[i * 3 + 2] = 1;
    }
  }
  var geom = new THREE.BufferGeometry();
  geom.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geom.setAttribute('color', new THREE.BufferAttribute(col, 3));
  var ptMat = new THREE.PointsMaterial({
    size: sizeMul, map: glowTex, blending: THREE.AdditiveBlending,
    depthWrite: false, transparent: true, vertexColors: true,
    sizeAttenuation: true, opacity: 0.9
  });
  var points = new THREE.Points(geom, ptMat);
  group.add(points);

  // Center sprite
  if (centerIdx >= 0) {
    var cn = layout.nodes[centerIdx];
    var spMat = new THREE.SpriteMaterial({
      map: goldTex, blending: THREE.AdditiveBlending,
      depthWrite: false, transparent: true, color: 0xffd700
    });
    var sprite = new THREE.Sprite(spMat);
    sprite.position.set(cn.x, cn.y, 0);
    sprite.scale.set(centerSize, centerSize, 1);
    group.add(sprite);
    _threeCenterSprite = sprite;
  }

  // Edges
  var ep = [];
  for (var i = 0; i < data.edges.length; i++) {
    var e = data.edges[i];
    var f = layout.map[e.from], t = layout.map[e.to];
    if (f && t) {
      var z1 = 0, z2 = 0;
      if (is3D) { z1 = (Math.random() - 0.5) * 80; z2 = (Math.random() - 0.5) * 80; }
      ep.push(f.x, f.y, z1, t.x, t.y, z2);
    }
  }
  if (ep.length > 0) {
    var eg = new THREE.BufferGeometry();
    eg.setAttribute('position', new THREE.Float32BufferAttribute(ep, 3));
    var em = new THREE.LineBasicMaterial({ color: 0x334488, transparent: true, opacity: 0.12 });
    var lines = new THREE.LineSegments(eg, em);
    group.add(lines);
    _threeLines = lines;
  }

  // Labels
  var lg = new THREE.Group();
  for (var i = 0; i < layout.nodes.length; i++) {
    var n = layout.nodes[i];
    var isC = n.id === '太初';
    var div = document.createElement('div');
    div.textContent = n.label;
    div.style.cssText =
      'color:' + (isC ? '#ffd700' : 'rgba(255,255,255,0.55)') + ';' +
      'font-size:' + (isC ? '14px' : '11px') + ';' +
      'font-weight:' + (isC ? 'bold' : 'normal') + ';' +
      'text-shadow:0 0 6px rgba(0,0,0,0.9);padding:2px 6px;' +
      'background:' + (isC ? 'rgba(0,0,0,0.5)' : 'rgba(0,0,0,0.25)') + ';' +
      'border-radius:3px;pointer-events:none;white-space:nowrap;' +
      'overflow:hidden;text-overflow:ellipsis;max-width:180px;';
    var label = new THREE.CSS2DObject(div);
    label.position.set(n.x, n.y + (isC ? 28 : n.size + 6), is3D ? (Math.random() - 0.5) * 80 : 0);
    lg.add(label);
  }
  group.add(lg);
  scene.add(group);

  _threeScene = scene; _threeCamera = camera; _threeRenderer = renderer;
  _threeControls = controls; _threeLabelRenderer = labelRenderer;
  _threePoints = points; _threeGroup = group; _threeReady = true;

  // Hover
  var raycaster = new THREE.Raycaster();
  var mouse = new THREE.Vector2();
  renderer.domElement.addEventListener('mousemove', function(e) {
    var rect = renderer.domElement.getBoundingClientRect();
    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(mouse, camera);
    var hits = raycaster.intersectObject(points, false);
    if (hits.length > 0 && hits[0].index !== undefined) {
      var idx = hits[0].index;
      if (idx >= 0 && idx < _threeNodeData.length) {
        if (idx !== _threeHoveredIdx) {
          _threeHoveredIdx = idx;
          renderer.domElement.style.cursor = 'pointer';
          ptMat.size = sizeMul * 1.4;
        }
        _showTooltip(_threeNodeData[idx].id, e.clientX, e.clientY);
        return;
      }
    }
    if (_threeHoveredIdx >= 0) {
      _threeHoveredIdx = -1;
      renderer.domElement.style.cursor = 'default';
      ptMat.size = sizeMul;
      _showTooltip(null, 0, 0);
    }
  });
  // Double-click focus
  renderer.domElement.addEventListener('dblclick', function(e) {
    raycaster.setFromCamera(mouse, camera);
    var hits = raycaster.intersectObject(points, false);
    if (hits.length > 0 && hits[0].index !== undefined) {
      var idx = hits[0].index;
      if (idx >= 0 && idx < _threeNodeData.length) {
        var n = _threeNodeData[idx];
        controls.target.set(n.x, n.y, 0);
        if (is3D) { camera.position.set(n.x + 100, n.y + 200, n.z + 300); }
        else { camera.position.set(n.x, n.y, 600); }
        controls.update();
        _showTooltip(n.id, e.clientX, e.clientY);
      }
    }
  });

  _animateThree();
}

function _animateThree() {
  if (!_threeReady || !_threeScene) return;
  var graphEl = document.getElementById('kb-graph');
  if (graphEl && _threeRenderer) {
    var w = graphEl.clientWidth, h = graphEl.clientHeight;
    if (w > 0 && h > 0 && (_threeRenderer.domElement.width !== w || _threeRenderer.domElement.height !== h)) {
      _threeCamera.aspect = w / h;
      _threeCamera.updateProjectionMatrix();
      _threeRenderer.setSize(w, h);
      if (_threeLabelRenderer) _threeLabelRenderer.setSize(w, h);
    }
  }
  if (_gfxSettings.view_mode !== '3d' && _gfxRotationSpeed > 0 && _threeGroup) {
    _threeGroup.rotation.z += 0.003 * _gfxRotationSpeed;
  }
  if (_threeControls) _threeControls.update();
  if (_threeRenderer && _threeScene && _threeCamera) {
    try {
      _threeRenderer.render(_threeScene, _threeCamera);
      if (_threeLabelRenderer) _threeLabelRenderer.render(_threeScene, _threeCamera);
    } catch(e) {}
  }
  _threeAnimId = requestAnimationFrame(_animateThree);
}

async function _gfxRefreshNebula(graphEl) {
  try {
    var ok = await _ensureThreeJs();
    if (!ok) {
      _gfxSettings.renderer = 'cpu';
      localStorage.setItem('taichu_gfx_renderer', 'cpu');
      showResult(__('gpu.fallback'), 'error');
      refreshNebula();
      return;
    }
    var limit = _gfxNodeLimit || 150;
    var resp = await fetch('/api/kb/graph?limit=' + limit);
    var data = await resp.json();
    if (data.error || !data.nodes || data.nodes.length === 0) {
      graphEl.innerHTML = '<div style="color:#888;text-align:center;padding-top:170px;font-size:13px;">' + __('nebula.empty') + '</div>';
      return;
    }
    _buildThreeScene(graphEl, data);
  } catch (e) {
    console.error('GPU Nebula error:', e);
    _gfxSettings.renderer = 'cpu';
    localStorage.setItem('taichu_gfx_renderer', 'cpu');
    refreshNebula();
  }
}

// ── Settings sidebar + Gfx settings ──
function initSettingsSidebar() {
  var items = document.querySelectorAll('.settings-sidebar-item');
  items.forEach(function(item) {
    item.addEventListener('click', function() {
      items.forEach(function(i) { i.classList.remove('active'); });
      item.classList.add('active');
      var panelId = item.dataset.settingsPanel;
      document.querySelectorAll('.settings-panel').forEach(function(p) { p.classList.remove('active'); });
      var panel = document.getElementById('settings-' + panelId);
      if (panel) panel.classList.add('active');
      if (panelId === 'graphics') renderGfxPanel();
      // 切换侧边栏时隐藏模型切换面板
      var mf=document.getElementById('model-switch-form');
      if(mf)mf.style.display='none';
      var ms=document.getElementById('model-provider-select');
      if(ms)ms.value='';
    });
  });
}

function loadGfxSettings() {
  _gfxSettings = {};
  var keys = ['renderer', 'view_mode', 'layout_mode', 'node_limit', 'rotation_speed', 'node_size'];
  keys.forEach(function(k) {
    var v = localStorage.getItem('taichu_gfx_' + k);
    if (v !== null) _gfxSettings[k] = v;
  });
  // Defaults
  if (!_gfxSettings.renderer) _gfxSettings.renderer = 'cpu';
  if (!_gfxSettings.view_mode) _gfxSettings.view_mode = '2d';
  if (!_gfxSettings.layout_mode || _gfxSettings.layout_mode === 'circle') _gfxSettings.layout_mode = 'spiral';
  if (!_gfxSettings.node_limit) _gfxSettings.node_limit = '150';
  if (!_gfxSettings.rotation_speed) _gfxSettings.rotation_speed = '1';
  if (!_gfxSettings.node_size) _gfxSettings.node_size = 'medium';
  applyGfxToNebula();
}

function applyGfxToNebula() {
  _gfxNodeLimit = parseInt(_gfxSettings.node_limit, 10) || 150;
  var speedMap = { off: 0, slow: 0.5, normal: 1, fast: 2 };
  _gfxRotationSpeed = speedMap[_gfxSettings.rotation_speed] || 1;
  var sizeMap = { small: 0.6, medium: 1, large: 1.6 };
  _gfxNodeSizeScale = sizeMap[_gfxSettings.node_size] || 1;
}

function saveGfxSetting(key, value) {
  _gfxSettings[key] = value;
  localStorage.setItem('taichu_gfx_' + key, value);
  applyGfxToNebula();
}

function renderGfxPanel() {
  var panel = document.getElementById('gfx-panel');
  if (!panel) return;
  var s = _gfxSettings;
  var rows = [
    { label: __('gfx.renderer'), key: 'renderer', opts: [
      { v: 'cpu', t: __('gfx.cpu') },
      { v: 'gpu', t: __('gfx.gpu') }
    ], hint: __('gfx.hint_renderer') },
    { label: __('gfx.view_mode'), key: 'view_mode', opts: [
      { v: '2d', t: __('gfx._2d') },
      { v: '3d', t: __('gfx._3d') }
    ], hint: __('gfx.hint_view') },
    { label: __('gfx.layout_mode'), key: 'layout_mode', opts: [
      { v: 'spiral', t: __('gfx.spiral') }
    ], hint: '' },
    { label: __('gfx.node_limit'), key: 'node_limit', opts: [
      { v: '50', t: '50' },
      { v: '150', t: '150' },
      { v: '300', t: '300' },
      { v: '500', t: '500' }
    ], hint: __('gfx.hint_limit') },
    { label: __('gfx.rotation_speed'), key: 'rotation_speed', opts: [
      { v: 'off', t: __('gfx.off') },
      { v: 'slow', t: __('gfx.slow') },
      { v: 'normal', t: __('gfx.normal') },
      { v: 'fast', t: __('gfx.fast') }
    ], hint: '' },
    { label: __('gfx.node_size'), key: 'node_size', opts: [
      { v: 'small', t: __('gfx.small') },
      { v: 'medium', t: __('gfx.medium') },
      { v: 'large', t: __('gfx.large') }
    ], hint: '' }
  ];
  var html = '';
  for (var i = 0; i < rows.length; i++) {
    var r = rows[i];
    var selected = s[r.key] || '';
    html += '<div class="gfx-row">';
    html += '  <div><div class="gfx-label">' + r.label + '</div>';
    if (r.hint) html += '  <div class="gfx-hint">' + r.hint + '</div>';
    html += '  </div>';
    html += '  <div class="gfx-control"><select data-gfx-key="' + r.key + '">';
    for (var j = 0; j < r.opts.length; j++) {
      var o = r.opts[j];
      html += '<option value="' + o.v + '"' + (o.v === selected ? ' selected' : '') + '>' + o.t + '</option>';
    }
    html += '</select></div></div>';
  }
  html += '<div style="margin-top:12px;text-align:center;"><button id="gfx-confirm-btn" style="background:#d4af37;color:#050816;border:none;padding:8px 24px;border-radius:4px;cursor:pointer;font-weight:600;font-size:13px;">' + __('common.confirm') + '</button></div>';
  panel.innerHTML = html;
  // Bind change events — only persist, no apply
  panel.querySelectorAll('select[data-gfx-key]').forEach(function(sel) {
    sel.addEventListener('change', function() {
      var key = this.dataset.gfxKey;
      var val = this.value;
      // Constraint: 3D requires GPU
      if (key === 'view_mode' && val === '3d' && _gfxSettings.renderer === 'cpu') {
        showResult(__('gfx.webgl_unavailable'), 'error');
        this.value = _gfxSettings[key];
        return;
      }
      localStorage.setItem('taichu_gfx_' + key, val);
    });
  });
  // Confirm button: apply all pending changes
  document.getElementById('gfx-confirm-btn').addEventListener('click', function() {
    console.log('[GFX] confirm clicked');
    panel.querySelectorAll('select[data-gfx-key]').forEach(function(sel) {
      _gfxSettings[sel.dataset.gfxKey] = sel.value;
      console.log('[GFX] set', sel.dataset.gfxKey, '=', sel.value);
    });
    applyGfxToNebula();
    refreshNebula();
    showResult(__('gfx.updated'), 'success');
  });
}

// ── Settings (rich 5-section, aligned with Tauri) ──
async function refreshSettings() {
  try {
    // Populate file stats + chroma
    var resp = await fetch('/api/stats');
    var s = await resp.json();

    // Knowledge section paths already hardcoded in HTML — skip

    // ChromaDB / DB Index
    var chromaEl = document.getElementById('set-chroma-status');
    var countEl = document.getElementById('set-chroma-count');
    var colsEl = document.getElementById('set-chroma-cols');
    if (chromaEl && s.chroma_available) {
      chromaEl.innerHTML = '<span class="ok">' + __('settings.chroma_online') + '</span>';
      if (countEl) countEl.textContent = s.chroma_count || 0;
      if (colsEl) colsEl.textContent = (s.chroma_collections || []).join(', ');
    } else if (chromaEl) {
      chromaEl.innerHTML = '<span class="err">' + __('settings.chroma_offline') + '</span>';
    }

    // File stats
    var wikiEl = document.getElementById('set-wiki-count');
    var archEl = document.getElementById('set-archive-count');
    var totalEl = document.getElementById('set-total-count');
    if (wikiEl) wikiEl.textContent = s.wiki_count || 0;
    if (archEl) archEl.textContent = s.archived_count || 0;
    if (totalEl) totalEl.textContent = s.total_count || 0;

    // Connection status (API probe)
    var apiStatusEl = document.getElementById('set-api-status');
    var wsStatusEl = document.getElementById('set-ws-status');
    if (apiStatusEl) apiStatusEl.innerHTML = '<span class="ok">' + __('ws.online') + '</span>';
    if (wsStatusEl) wsStatusEl.innerHTML = '<span class="err">' + __('ws.offline') + '</span>';

    // Runtime metrics section
    var metricsEl = document.getElementById('settings-metrics');
    if (metricsEl) {
      try {
        var mr = await fetch('/api/metrics');
        var metrics = await mr.json();
        if (metrics.graph) {
          metricsEl.innerHTML = '<table style="width:100%;font-size:12px;border-collapse:collapse;">' +
            '<tr><td style="color:rgba(255,255,255,0.5);padding:4px 0;">' + __('metrics.retrieval_count') + '</td><td style="text-align:right;">' + (metrics.retrieval.queries || 0) + '</td></tr>' +
            '<tr><td style="color:rgba(255,255,255,0.5);padding:4px 0;">' + __('metrics.avg_latency') + '</td><td style="text-align:right;">' + Math.round(metrics.retrieval.avg_latency_ms || 0) + 'ms</td></tr>' +
            '<tr><td style="color:rgba(255,255,255,0.5);padding:4px 0;">' + __('metrics.graph_nodes') + '</td><td style="text-align:right;">' + metrics.graph.nodes + '</td></tr>' +
            '<tr><td style="color:rgba(255,255,255,0.5);padding:4px 0;">' + __('metrics.orphan_nodes') + '</td><td style="text-align:right;">' + metrics.graph.orphan_nodes + '</td></tr>' +
            '<tr><td style="color:rgba(255,255,255,0.5);padding:4px 0;">' + __('metrics.avg_neighbors') + '</td><td style="text-align:right;">' + metrics.graph.avg_neighbors + '</td></tr>' +
            '<tr><td style="color:rgba(255,255,255,0.5);padding:4px 0;">' + __('metrics.eventbus') + '</td><td style="text-align:right;">' + (metrics.runtime.eventbus_emits || 0) + '</td></tr>' +
            '</table>' +
            '<div style="margin-top:10px;"><button onclick="runPipelineTrace()" style="background:#d4af37;color:#050816;border:none;padding:5px 14px;border-radius:4px;cursor:pointer;font-size:12px;">' + __('pipeline.run') + '</button></div>' +
            '<div id="pipeline-trace" style="margin-top:6px;font-size:11px;"></div>';
        } else {
          metricsEl.innerHTML = '<div style="color:rgba(255,255,255,0.5);font-style:italic;font-size:12px;">' + __('metrics.unavailable') + '</div>';
        }
      } catch(e) {
        metricsEl.innerHTML = '<div style="color:rgba(255,255,255,0.5);font-style:italic;font-size:12px;">' + __('metrics.load_fail') + '</div>';
      }
    }
    // Model panel
    refreshModelPanel();
    // Sidebar + gfx settings
    initSettingsSidebar();
    loadGfxSettings();
    if (document.getElementById('settings-graphics').classList.contains('active')) {
      renderGfxPanel();
    }
    // Language select
    var langSel = document.getElementById('lang-select');
    var langBtn = document.getElementById('lang-confirm');
    if (langSel) {
      langSel.value = _lang;
    }
    if (langBtn) {
      langBtn.onclick = function() {
        _lang = langSel.value;
        localStorage.setItem('taichu_lang', _lang);
        updateLangUI();
      };
    }
  } catch (e) {
    // Settings load failed — just show nothing extra
  }
}



// ── Phase 2 Pipeline Trace ──
async function runPipelineTrace() {
  var el = document.getElementById('pipeline-trace');
  if (!el) return;
  el.innerHTML = __('pipeline.running');
  try {
    var resp = await fetch('/api/pipeline/trace?q=' + encodeURIComponent('transformer attention'));
    var d = await resp.json();
    if (d.error) { el.innerHTML = '<span style="color:#f87171;">' + d.error + '</span>'; return; }
    var html = '<table style="width:100%;font-size:11px;border-collapse:collapse;">';
    var stages = [
      ['query_parser', __('pipeline.query_parser')],
      ['vector_search', __('pipeline.vector_search')],
      ['graph_expand', __('pipeline.graph_expand')],
      ['ontology_filter', __('pipeline.ontology_filter')],
      ['rerank', __('pipeline.rerank')],
      ['context_builder', __('pipeline.context_builder')],
    ];
    for (var s of stages) {
      var ms = d.timers[s[0]] || 0;
      var color = ms > 1000 ? '#f87171' : ms > 200 ? '#fbbf24' : '#4ade80';
      var badge = ms > 1000 ? ' ✗' : ms > 200 ? ' ⚠' : ' ✓';
      html += '<tr><td style="color:rgba(255,255,255,0.5);padding:1px 0;">' + s[1] + '</td><td style="text-align:right;color:' + color + ';">' + ms + 'ms' + badge + '</td></tr>';
    }
    html += '<tr><td style="border-top:1px solid rgba(255,255,255,0.06);padding:1px 0;font-weight:600;">' + __('pipeline.total') + '</td><td style="border-top:1px solid rgba(255,255,255,0.06);text-align:right;font-weight:600;">' + d.total_ms + 'ms</td></tr>';
    html += '<tr><td style="color:rgba(255,255,255,0.5);padding:1px 0;">' + __('pipeline.results') + '</td><td style="text-align:right;">' + d.result_count + '</td></tr>';
    if (d.graph_nodes_expanded > 0) {
      html += '<tr><td style="color:rgba(255,255,255,0.5);padding:1px 0;">' + __('pipeline.graph_expanded') + '</td><td style="text-align:right;">' + d.graph_nodes_expanded + ' ' + __('pipeline.nodes') + '</td></tr>';
    }
    html += '</table>';
    html += '<div style="margin-top:6px;font-size:10px;color:rgba(255,255,255,0.3);">' + __('pipeline.reference') + '</div>';
    el.innerHTML = html;
  } catch(e) {
    el.innerHTML = '<span style="color:#f87171;">' + __('settings.api_down') + '</span>';
  }
}

var _providersData=[];

function refreshModelPanel(){
  var panel=document.getElementById('model-panel');
  if(!panel)return;
  fetch('/api/models').then(function(r){return r.json();}).then(function(d){
    _providersData=d.providers||[];
    var html='<div style="margin-bottom:10px;font-weight:600;color:rgba(255,255,255,0.8);font-size:13px;">' + __('model.current') + '</div>';
    var roles={compile:__('model.role_compile'),query:__('model.role_query'),reasoning:__('model.role_reasoning'),embedding:__('model.role_embedding'),vision:__('model.role_vision')};
    var roleOrder=['compile','query','reasoning','embedding','vision'];
    for(var i=0;i<roleOrder.length;i++){
      var role=roleOrder[i];
      var c=d.current[role];
      if(!c||!c.model)continue;
      html+='<div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.04);font-size:12px;">';
      html+='<span style="color:rgba(255,255,255,0.5);">'+(roles[role]||role)+'</span>';
      html+='<span style="color:#7dd3fc;font-family:monospace;font-size:11px;">'+c.model.substring(0,30)+'</span>';
      html+='</div>';
    }
    html+='<div style="margin-top:14px;font-weight:600;color:rgba(255,255,255,0.8);font-size:13px;margin-bottom:8px;">' + __('model.switch_title') + '</div>';
    if(_providersData.length>0){
      html+='<div style="margin-bottom:10px;"><select id="model-provider-select" style="width:100%;padding:8px 10px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:4px;color:#fff;font-size:13px;outline:none;cursor:pointer;';
      html+='-webkit-appearance:none;appearance:none;">';
      html+='<option value="" style="color:#222;background:#f0f0f0;">' + __('model.select_provider') + '</option>';
      for(var i=0;i<_providersData.length;i++){
        var p=_providersData[i];
        html+='<option value="'+esc(p.id)+'" style="color:#222;background:#f0f0f0;">'+esc(p.name)+'</option>';
      }
      html+='</select></div>';
    }
    // 表单区域（由 select 切换时填充）
    html+='<div id="model-switch-form" style="display:none;padding:12px;background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.1);border-radius:6px;">';
    html+='  <div id="switch-provider-name" style="margin-bottom:8px;font-weight:600;color:#7dd3fc;font-size:13px;"></div>';
    html+='  <div style="margin-bottom:6px;"><label style="display:block;font-size:11px;color:rgba(255,255,255,0.4);margin-bottom:2px;">' + __('model.base_url') + '</label>';
    html+='    <input id="switch-base-url" type="text" style="width:100%;padding:7px 10px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:4px;color:#fff;font-size:12px;outline:none;box-sizing:border-box;"></div>';
    html+='  <div style="margin-bottom:6px;"><label style="display:block;font-size:11px;color:rgba(255,255,255,0.4);margin-bottom:2px;">' + __('model.api_endpoint') + '</label>';
    html+='    <input id="switch-endpoint" type="text" style="width:100%;padding:7px 10px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:4px;color:#fff;font-size:12px;outline:none;box-sizing:border-box;"></div>';
    html+='  <div style="margin-bottom:8px;"><label style="display:block;font-size:11px;color:rgba(255,255,255,0.4);margin-bottom:2px;">' + __('model.api_key') + '</label>';
    html+='    <input id="switch-api-key" type="text" style="width:100%;padding:7px 10px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:4px;color:#fff;font-size:12px;outline:none;box-sizing:border-box;"></div>';
    html+='  <div style="display:flex;gap:6px;">';
    html+='    <button id="switch-confirm-btn" style="flex:1;padding:6px;background:#7dd3fc;color:#050816;border:none;border-radius:4px;cursor:pointer;font-weight:600;font-size:12px;">' + __('model.confirm_switch') + '</button>';
    html+='    <button id="switch-cancel-btn" style="flex:1;padding:6px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);color:rgba(255,255,255,0.5);border-radius:4px;cursor:pointer;font-size:12px;">' + __('model.cancel') + '</button>';
    html+='  </div><div id="switch-result" style="margin-top:8px;font-size:12px;"></div>';
    html+='</div>';
    panel.innerHTML=html;

    var sel=document.getElementById('model-provider-select');
    var form=document.getElementById('model-switch-form');
    if(sel&&form){
      sel.addEventListener('change',function(){
        var pid=this.value;
        if(!pid){form.style.display='none';return;}
        var provider=null;
        for(var i=0;i<_providersData.length;i++){if(_providersData[i].id===pid){provider=_providersData[i];break;}}
        if(!provider)return;
        document.getElementById('switch-provider-name').textContent=__('model.switching_to')+provider.name;
        document.getElementById('switch-base-url').value=provider.base_url||'';
        document.getElementById('switch-endpoint').value=provider.chat_endpoint||'/v1/chat/completions';
        document.getElementById('switch-api-key').value='';
        document.getElementById('switch-result').innerHTML='';
        form.style.display='block';
      });
    }
    document.getElementById('switch-confirm-btn').addEventListener('click',function(){confirmModelSwitch();});
    document.getElementById('switch-cancel-btn').addEventListener('click',function(){
      document.getElementById('model-switch-form').style.display='none';
      if(sel)sel.value='';
    });
  }).catch(function(){panel.innerHTML='<div style="color:rgba(255,255,255,0.3);font-style:italic;">' + __('model.unavailable') + '</div>';});
}

function confirmModelSwitch(){
  var sel=document.getElementById('model-provider-select');
  var resultEl=document.getElementById('switch-result');
  if(!sel||!resultEl)return;
  var providerId=sel.value;
  if(!providerId){resultEl.innerHTML='<span style="color:#f87171;">' + __('model.no_provider') + '</span>';return;}
  var baseUrl=document.getElementById('switch-base-url')?document.getElementById('switch-base-url').value.trim():'';
  var endpoint=document.getElementById('switch-endpoint')?document.getElementById('switch-endpoint').value.trim():'';
  var apiKey=document.getElementById('switch-api-key')?document.getElementById('switch-api-key').value.trim():'';
  resultEl.innerHTML=__('model.switching') + '...';
  fetch('/api/models/switch',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({provider_id:providerId,base_url:baseUrl,endpoint:endpoint,api_key:apiKey})}).then(function(r){return r.json();}).then(function(d){
    if(d.ok){resultEl.innerHTML='<span style="color:#4ade80;">✔ '+esc(d.message)+'</span>';setTimeout(function(){refreshModelPanel();},1500);}
    else{resultEl.innerHTML='<span style="color:#f87171;">❌ '+esc(d.error)+'</span>';}
  }).catch(function(){resultEl.innerHTML='<span style="color:#f87171;">' + __('model.network_error') + '</span>';});
}

// ── WebSocket 连接 ──
var _ws = null;
function connectWS() {
  try {
    _ws = new WebSocket('ws://' + location.host + '/ws');
    _ws.onopen = function() {
      var el = document.getElementById('set-ws-status');
      if (el) el.innerHTML = '<span class="ok">' + __('ws.online') + '</span>';
    };
    _ws.onmessage = function(ev) {
      try {
        var d = JSON.parse(ev.data);
        // graph:updated → 自动刷新星云
        if (d.event === 'graph:updated' || d.event === 'memory:stored' || d.event === 'memory:deleted') {
          refreshNebula();
        }
      } catch(e) {}
    };
    _ws.onclose = function() {
      var el = document.getElementById('set-ws-status');
      if (el) el.innerHTML = '<span class="err">' + __('ws.offline') + '</span>';
      setTimeout(connectWS, 3000);
    };
  } catch(e) {
    setTimeout(connectWS, 3000);
  }
}

// ── Search filter & group mode event bindings ──
function _initSearchFilters() {
  // Type filter checkboxes
  var typeCbs = document.querySelectorAll('#type-filter-row input[type="checkbox"]');
  typeCbs.forEach(function(cb) {
    cb.addEventListener('change', function() {
      if (_lastSearchData) {
        var html = _renderSearchResults(_lastSearchData);
        var resultEl = document.getElementById('search-result');
        if (resultEl && html) {
          // Re-wrap
          resultEl.innerHTML = '<div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:16px;border:1px solid rgba(255,255,255,0.06);"><div style="font-weight:600;color:#d4af37;margin-bottom:10px;font-size:14px;">' + (_searchMode === 'ask' ? __('search.ask_result') : __('search.semantic_result')) + '</div>' + html + '</div>';
        } else if (resultEl && !html) {
          resultEl.innerHTML = '<div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:16px;border:1px solid rgba(255,255,255,0.06);"><div style="font-weight:600;color:#d4af37;margin-bottom:10px;font-size:14px;">' + (_searchMode === 'ask' ? __('search.ask_result') : __('search.semantic_result')) + '</div><div style="padding:12px;color:rgba(255,255,255,0.4);">' + __('search.no_result') + '</div></div>';
        }
      }
    });
  });
  // Group mode buttons
  var groupBtns = document.querySelectorAll('#group-mode-row .group-mode-btn');
  groupBtns.forEach(function(btn) {
    btn.addEventListener('click', function() {
      groupBtns.forEach(function(b) { b.classList.remove('active'); });
      btn.classList.add('active');
      _searchGroupMode = btn.dataset.group || 'type';
      if (_lastSearchData) {
        var html = _renderSearchResults(_lastSearchData);
        var resultEl = document.getElementById('search-result');
        if (resultEl && html) {
          resultEl.innerHTML = '<div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:16px;border:1px solid rgba(255,255,255,0.06);"><div style="font-weight:600;color:#d4af37;margin-bottom:10px;font-size:14px;">' + (_searchMode === 'ask' ? __('search.ask_result') : __('search.semantic_result')) + '</div>' + html + '</div>';
        } else if (resultEl && !html) {
          resultEl.innerHTML = '<div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:16px;border:1px solid rgba(255,255,255,0.06);"><div style="font-weight:600;color:#d4af37;margin-bottom:10px;font-size:14px;">' + (_searchMode === 'ask' ? __('search.ask_result') : __('search.semantic_result')) + '</div><div style="padding:12px;color:rgba(255,255,255,0.4);">' + __('search.no_result') + '</div></div>';
        }
      }
    });
  });
}

// ── Agent 记忆仪表盘 ──

var _memoryPieChart = null;
var _memoryTypeChart = null;

async function refreshMemoryDashboard() {
  try {
    // Fetch agent registry + memory sessions in parallel
    var [agentResp, memResp] = await Promise.all([
      fetch('/api/agents'),
      fetch('/api/kb/memory/sessions?limit=100')
    ]);
    var agentData = await agentResp.json();
    var memData = await memResp.json();
    var sessions = memData.sessions || [];
    var agents = agentData.agents || [];

    // Agent count from registry
    var onlineCount = agents.filter(function(a) { return a.online; }).length;
    var acEl = document.getElementById('mem-agent-count');
    if (acEl) {
      acEl.querySelector('div:first-child').textContent = agents.length;
      var labelEl = acEl.querySelector('div:last-child');
      if (labelEl) labelEl.textContent = '接入 Agent (' + onlineCount + ' 在线)';
    }

    // Count by agent from memory sessions
    var agentMap = {};
    var totalMemories = 0;
    sessions.forEach(function(s) {
      var aid = s.agent_id || 'unknown';
      if (!agentMap[aid]) agentMap[aid] = { sessions: 0, memories: 0, types: {}, last: '' };
      agentMap[aid].sessions += 1;
      agentMap[aid].memories += (s.count || 0);
      totalMemories += (s.count || 0);
      if (s.last_timestamp > agentMap[aid].last) agentMap[aid].last = s.last_timestamp;
      (s.types || []).forEach(function(t) {
        agentMap[aid].types[t] = (agentMap[aid].types[t] || 0) + 1;
      });
    });

    document.getElementById('mem-total-count').querySelector('div:first-child').textContent = totalMemories;
    document.getElementById('mem-session-count').querySelector('div:first-child').textContent = sessions.length;

    // Pie chart
    var ctx = document.getElementById('memory-agent-chart');
    if (ctx) {
      var labels = Object.keys(agentMap);
      var values = labels.map(function(l) { return agentMap[l].memories; });
      var colors = ['#7dd3fc','#6ee7b7','#fbbf24','#f97316','#a78bfa','#f472b6','#94a3b8'];

      if (_memoryPieChart) _memoryPieChart.destroy();
      _memoryPieChart = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: labels,
          datasets: [{
            data: values,
            backgroundColor: colors.slice(0, labels.length),
            borderColor: '#050816',
            borderWidth: 2
          }]
        },
        options: {
          responsive: false,
          plugins: {
            legend: { display: false }
          }
        }
      });
    }

    // Type distribution pie chart
    var typeCtx = document.getElementById('memory-type-chart');
    if (typeCtx && sessions.length > 0) {
      var typeMap = {};
      sessions.forEach(function(s) {
        (s.types || []).forEach(function(t) {
          typeMap[t] = (typeMap[t] || 0) + 1;
        });
      });
      var typeLabels = Object.keys(typeMap);
      var typeValues = typeLabels.map(function(t) { return typeMap[t]; });
      var typeColors = ['#7dd3fc','#6ee7b7','#fbbf24','#f97316','#a78bfa','#f472b6','#94a3b8'];

      if (_memoryTypeChart) _memoryTypeChart.destroy();
      _memoryTypeChart = new Chart(typeCtx, {
        type: 'pie',
        data: {
          labels: typeLabels,
          datasets: [{
            data: typeValues,
            backgroundColor: typeColors.slice(0, typeLabels.length),
            borderColor: '#050816',
            borderWidth: 2
          }]
        },
        options: {
          responsive: false,
          plugins: {
            legend: { display: false }
          }
        }
      });
    }

    // Recent sessions list
    var recentEl = document.getElementById('memory-recent-list');
    if (recentEl) {
      var recent = sessions.slice(0, 10);
      var html = recent.map(function(s) {
        var ts = s.last_timestamp ? s.last_timestamp.slice(0, 19).replace('T', ' ') : '--';
        return '<div style="padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04);display:flex;justify-content:space-between;">' +
          '<span><span style="color:#7dd3fc;">' + esc(s.agent_id) + '</span> / ' + esc(s.session_id) + '</span>' +
          '<span style="color:rgba(255,255,255,0.4);font-size:12px;">' + s.count + '条 · ' + ts + '</span></div>';
      }).join('');
      recentEl.innerHTML = html || '<div style="color:rgba(255,255,255,0.3);font-style:italic;">'+__('memory.no_data')+'</div>';
    }

    // Agent table
    var tbody = document.getElementById('memory-agent-tbody');
    if (tbody) {
      var rows = Object.keys(agentMap).sort().map(function(aid) {
        var a = agentMap[aid];
        var ts = a.last ? a.last.slice(0, 19).replace('T', ' ') : '--';
        var types = Object.keys(a.types).join(', ');
        return '<tr style="border-bottom:1px solid rgba(255,255,255,0.04);">' +
          '<td style="padding:8px 12px;color:#7dd3fc;">' + esc(aid) + '</td>' +
          '<td style="padding:8px 12px;">' + a.sessions + '</td>' +
          '<td style="padding:8px 12px;">' + a.memories + '</td>' +
          '<td style="padding:8px 12px;color:rgba(255,255,255,0.5);font-size:12px;">' + esc(types) + '</td>' +
          '<td style="padding:8px 12px;color:rgba(255,255,255,0.4);font-size:12px;">' + ts + '</td>' +
          '</tr>';
      }).join('');
      tbody.innerHTML = rows || '<tr><td colspan="5" style="padding:20px;text-align:center;color:rgba(255,255,255,0.3);">'+__('memory.no_data')+'</td></tr>';
    }
  } catch(e) {
    console.error('[memory dashboard]', e);
    ['memory-recent-list','memory-agent-tbody'].forEach(function(id) {
      var el = document.getElementById(id);
      if (el) el.innerHTML = '<div style="color:rgba(255,255,255,0.3);font-style:italic;">'+__('aging.load_fail')+'</div>';
    });
  }
}

// ── 老化仪表盘 ──

var _agingPieChart = null;

async function refreshAgingDashboard() {
  try {
    var resp = await fetch('/api/kb/aging/report');
    var report = await resp.json();

    document.getElementById('aging-total').querySelector('div:first-child').textContent = report.total_articles || 0;
    document.getElementById('aging-notice').querySelector('div:first-child').textContent = (report.tier_distribution && report.tier_distribution.notice) || 0;
    document.getElementById('aging-aging').querySelector('div:first-child').textContent = (report.tier_distribution && report.tier_distribution.aging) || 0;
    document.getElementById('aging-stale').querySelector('div:first-child').textContent = (report.tier_distribution && report.tier_distribution.stale) || 0;

    // Pie chart
    var ctx = document.getElementById('aging-pie-chart');
    if (ctx && report.tier_distribution) {
      var d = report.tier_distribution;
      var labels = ['🟢 Active', '🟡 Notice', '🟠 Aging', '🔴 Stale'];
      var values = [d.active || 0, d.notice || 0, d.aging || 0, d.stale || 0];
      var colors = ['#22c55e', '#fbbf24', '#f97316', '#ef4444'];

      if (_agingPieChart) _agingPieChart.destroy();
      _agingPieChart = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: labels,
          datasets: [{
            data: values,
            backgroundColor: colors,
            borderColor: '#050816',
            borderWidth: 2
          }]
        },
        options: {
          responsive: false,
          plugins: {
            legend: { display: false }
          }
        }
      });
    }

    // Top aged list
    var topResp = await fetch('/api/kb/aging?limit=20');
    var topData = await topResp.json();
    var topResults = topData.results || [];

    var tbody = document.getElementById('aging-top-tbody');
    if (tbody) {
      var rows = topResults.map(function(r, i) {
        var tierColor = r.tier === 'stale' ? '#ef4444' : r.tier === 'aging' ? '#f97316' : r.tier === 'notice' ? '#fbbf24' : '#22c55e';
        return '<tr style="border-bottom:1px solid rgba(255,255,255,0.04);">' +
          '<td style="padding:8px 12px;color:rgba(255,255,255,0.4);">' + (i+1) + '</td>' +
          '<td style="padding:8px 12px;max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="' + esc(r.file) + '">' + esc(r.file) + '</td>' +
          '<td style="padding:8px 12px;font-weight:600;color:' + tierColor + ';">' + r.score.toFixed(3) + '</td>' +
          '<td style="padding:8px 12px;"><span style="display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;background:' + tierColor + '22;color:' + tierColor + ';">' + r.tier + '</span></td>' +
          '<td style="padding:8px 12px;color:rgba(255,255,255,0.5);">' + (r.breakdown ? r.breakdown.time_decay.toFixed(3) : '--') + '</td>' +
          '<td style="padding:8px 12px;color:rgba(255,255,255,0.5);">' + (r.breakdown ? r.breakdown.frequency.toFixed(3) : '--') + '</td>' +
          '<td style="padding:8px 12px;color:rgba(255,255,255,0.5);">' + (r.breakdown ? r.breakdown.confidence.toFixed(3) : '--') + '</td>' +
          '</tr>';
      }).join('');
      tbody.innerHTML = rows || '<tr><td colspan="7" style="padding:20px;text-align:center;color:rgba(255,255,255,0.3);">'+__('memory.no_data')+'</td></tr>';
    }

    var aar = document.getElementById('aging-action-result'); if(aar) aar.textContent = __('aging.updated') + new Date().toLocaleTimeString();
  } catch(e) {
    console.error('[aging dashboard]', e);
    var aar = document.getElementById('aging-action-result'); if(aar) aar.textContent = __('aging.load_fail') + e.message;
  }
}

async function applyAgingFlags() {
  var btn = event && event.target ? event.target : document.querySelector('#aging-action-result');
  var resultEl = document.getElementById('aging-action-result');
  if (resultEl) resultEl.textContent = '标记中...';
  try {
    var resp = await fetch('/api/kb/aging/apply', { method: 'POST' });
    var data = await resp.json();
    if (resultEl) resultEl.textContent = __('aging.batch_mark') + ': ' + (data.total || 0) + ' files, ' + (data.flagged || 0) + ' flagged';
    refreshAgingDashboard();
  } catch(e) {
    if (resultEl) resultEl.textContent = __('aging.load_fail') + e.message;
  }
}

// ── Init ──
try {
  document.querySelectorAll('#content-area > div').forEach(function(d){d.style.display='none';});
  document.getElementById('tab-home').style.display='block';
  refreshStats();
  refreshNebula();
  updateLangUI();
  _initSearchFilters();
  connectWS();
  // Dashboard auto-refresh timers
  var _memoryTimer = null, _agingTimer = null;
  document.querySelectorAll('#navbar .nav-item').forEach(function(tab) {
    tab.addEventListener('click', function() {
      var tabId = this.dataset.tab;
      if (tabId === 'memory') {
        clearInterval(_agingTimer); _agingTimer = null;
        setTimeout(refreshMemoryDashboard, 100);
        if (!_memoryTimer) _memoryTimer = setInterval(refreshMemoryDashboard, 60000);
      } else if (tabId === 'aging') {
        clearInterval(_memoryTimer); _memoryTimer = null;
        setTimeout(refreshAgingDashboard, 100);
        if (!_agingTimer) _agingTimer = setInterval(refreshAgingDashboard, 60000);
      } else {
        clearInterval(_memoryTimer); _memoryTimer = null;
        clearInterval(_agingTimer); _agingTimer = null;
      }
    });
  });
} catch(e) { console.error('[init]', e); }
