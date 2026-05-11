// ── Tab navigation ──
function switchTab(tab) {
  document.querySelectorAll('.topbar-item').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.panel-section').forEach(el => el.classList.add('hidden'));
  const tabEl = document.querySelector(`[data-tab="${tab}"]`);
  if (tabEl) tabEl.classList.add('active');
  const section = document.getElementById('section-' + tab);
  if (section) section.classList.remove('hidden');
  if (tab === 'nebula') {
    requestAnimationFrame(function() {
      requestAnimationFrame(function() { refreshNebula(); });
    });
  }
  if (tab === 'links') setTimeout(refreshLinkTable, 50);
  if (tab === 'entries') { _wikiPage = 0; setTimeout(refreshStats, 50); }
  if (tab === 'overview') { setTimeout(refreshPending, 100); }
  if (tab === 'settings') { setTimeout(refreshSettings, 100); }
}

// ── Stats refresh (paginated) ──
let _wikiPage = 0;
const _pageSize = 50;
let _lastStats = null;

async function refreshStats() {
  try {
    const resp = await fetch('/api/stats');
    const s = await resp.json();
    _lastStats = s;
    document.getElementById('stats-bar').innerHTML =
      '<div class="stat-card"><div class="num">' + s.total_count + '</div><div class="label">总词条</div></div>' +
      '<div class="stat-card"><div class="num">' + s.wiki_count + '</div><div class="label">核心</div></div>' +
      '<div class="stat-card"><div class="num">' + s.archived_count + '</div><div class="label">归档</div></div>';
    var wBody = document.getElementById('wiki-panel');
    _wikiPage = 0;
    renderWikiPage();
  } catch (e) { console.error('Stats error:', e); }
}

function renderWikiPage() {
  var s = _lastStats;
  if (!s) return;
  var wBody = document.getElementById('wiki-panel');
  if (!wBody) {
    wBody = document.createElement('div');
    wBody.id = 'wiki-panel';
    document.getElementById('section-entries').appendChild(wBody);
  }
  const core = s.wiki_articles || [];
  const archived = s.archived_articles || [];
  const start = _wikiPage * _pageSize;
  const total = core.length + archived.length;
  const totalPages = Math.ceil(total / _pageSize) || 1;
  let html = '<div class="wiki-header"><span class="wiki-count">' + total + ' 个词条</span><span class="wiki-page">第 ' + (_wikiPage + 1) + '/' + totalPages + ' 页</span></div>';
  for (var i = start; i < start + _pageSize && i < core.length; i++) {
    var name = esc(core[i]).replace(/^archive-/i, '');
    html += '<div class="item"><span class="dot core"></span><span class="name">' + name + '</span><span class="tag">核心</span></div>';
  }
  for (var i = Math.max(0, start - core.length); i < start + _pageSize - core.length && i < archived.length; i++) {
    var name = esc(archived[i]).replace(/^archive-/i, '');
    html += '<div class="item"><span class="dot archive"></span><span class="name">' + name + '</span><span class="tag">归档</span></div>';
  }
  if (total > _pageSize) {
    html += '<div class="page-bar">';
    if (_wikiPage > 0) html += '<button onclick="_wikiPage--;renderWikiPage()">← 上一页</button>';
    if (start + _pageSize < total) html += '<button onclick="_wikiPage++;renderWikiPage()">下一页 →</button>';
    html += '</div>';
  }
  wBody.innerHTML = html;
}

// ── Upload ──
const DROPZONE = document.getElementById('dropzone');
const FILE_INPUT = document.getElementById('file-input');
if (DROPZONE) {
  DROPZONE.addEventListener('dragover', e => { e.preventDefault(); DROPZONE.classList.add('dragover'); });
  DROPZONE.addEventListener('dragleave', () => DROPZONE.classList.remove('dragover'));
  DROPZONE.addEventListener('drop', e => { e.preventDefault(); DROPZONE.classList.remove('dragover'); handleFiles(e.dataTransfer.files); });
  DROPZONE.addEventListener('click', () => FILE_INPUT.click());
  FILE_INPUT.addEventListener('change', () => handleFiles(FILE_INPUT.files));
}

async function handleFiles(files) {
  const formData = new FormData();
  let fileCount = 0;
  const allowed = ['.md','.pdf','.docx','.pptx','.html','.htm','.txt','.csv','.xlsx','.epub','.png','.jpg','.jpeg','.webp','.gif','.bmp','.py','.js','.ts','.yaml','.toml'];
  for (const f of files) {
    const ext = '.' + f.name.split('.').pop().toLowerCase();
    if (allowed.includes(ext)) { formData.append('files', f); fileCount++; }
  }
  if (fileCount === 0) { showResult('不支持的文件格式', 'error'); return; }
  showLoading('上传 ' + fileCount + ' 个文件中...');
  try {
    const resp = await fetch('/upload', { method: 'POST', body: formData });
    const d = await resp.json();
    hideLoading();
    if (d.ok) {
      showResult(d.note || ('上传了 ' + d.md_count + ' 个 .md' + (d.other_count ? '，' + d.other_count + ' 个待编译' : '')), 'success');
      refreshStats(); refreshNebula(); refreshPending();
    } else {
      showResult('上传失败：' + (d.error || '未知错误'), 'error');
    }
  } catch (e) {
    hideLoading();
    showResult('上传出错：' + e.message, 'error');
  }
}

// ── Pending files + Compile ──
async function refreshPending() {
  try {
    const resp = await fetch('/api/kb/pending');
    const d = await resp.json();
    const panel = document.getElementById('pending-panel');
    const badge = document.getElementById('pending-badge');
    if (!panel) return;
    if (badge) badge.textContent = d.count > 0 ? '(' + d.count + ')' : '';
    if (d.count === 0) { panel.innerHTML = '<div class="empty">✦ 没有待处理文件</div>'; return; }
    let html = '';
    d.pending.forEach(function(f) {
      const sizeStr = f.size > 1024 ? (f.size / 1024).toFixed(1) + 'KB' : f.size + 'B';
      html += '<div class="item"><span class="dot pending"></span><span class="name">' + esc(f.name) + '</span><span style="font-size:11px;color:var(--dim);margin-left:8px;">' + sizeStr + '</span><button onclick="deletePending(\'' + esc(f.name) + '\')" style="margin-left:auto;background:none;border:none;color:#e8963e;font-size:14px;cursor:pointer;padding:2px 6px;" title="删除">✕</button></div>';
    });
    panel.innerHTML = html;
  } catch (e) { console.error('Pending error:', e); }
}

async function triggerCompile() {
  showLoading('⚡ 编译中，请稍候...（可能需要 1-2 分钟）');
  try {
    const resp = await fetch('/api/kb/compile', { method: 'POST' });
    const d = await resp.json();
    hideLoading();
    if (d.ok) {
      const count = d.converted || 0;
      showResult('✔ 编译完成，' + count + ' 个文件已转换', 'success');
    } else {
      showResult('编译失败：' + (d.error || '未知错误'), 'error');
    }
  } catch (e) {
    hideLoading();
    showResult('编译出错：' + e.message, 'error');
  }
  refreshPending();
  refreshStats();
}

function showLoading(msg) {
  var overlay = document.getElementById('loading-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    document.body.appendChild(overlay);
  }
  overlay.innerHTML = '<div style="text-align:center;"><div class="spinner"></div><div style="margin-top:16px;color:var(--text);font-size:14px;">' + (msg || '处理中...') + '</div></div>';
  overlay.style.display = 'flex';
}

function hideLoading() {
  var overlay = document.getElementById('loading-overlay');
  if (overlay) overlay.style.display = 'none';
}

function showResult(msg, type) {
  const el = document.getElementById('result');
  el.className = type;
  el.innerHTML = msg;
  setTimeout(() => { el.className = ''; el.innerHTML = ''; }, 6000);
}

function esc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

// ── Delete pending file ──
async function deletePending(filename) {
  if (!confirm('确定要删除 ' + filename + ' 吗？')) return;
  showLoading('正在删除...');
  try {
    const resp = await fetch('/api/kb/pending/delete', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({filename: filename})
    });
    const d = await resp.json();
    hideLoading();
    if (d.ok) {
      showResult('已删除: ' + filename, 'success');
      refreshPending();
    } else {
      showResult('删除失败: ' + (d.error || '未知错误'), 'error');
    }
  } catch (e) {
    hideLoading();
    showResult('删除出错: ' + e.message, 'error');
  }
}

// ── Search (semantic + RAG) ──
let _searchMode = 'search';
function setSearchMode(mode) {
  _searchMode = mode;
  ['mode-search','mode-ask'].forEach(function(id) {
    const el = document.getElementById(id);
    if (!el) return;
    const active = (mode === 'search' && id === 'mode-search') || (mode === 'ask' && id === 'mode-ask');
    el.style.background = active ? 'var(--gold)' : 'var(--surface)';
    el.style.color = active ? '#fff' : 'var(--dim)';
  });
}

async function doSearch() {
  const q = document.getElementById('search-input').value.trim();
  if (!q) return;
  const resultEl = document.getElementById('search-result');
  showLoading('🔍 搜索中...');
  try {
    const resp = await fetch('/api/kb/' + (_searchMode === 'ask' ? 'ask' : 'search') + '?q=' + encodeURIComponent(q));
    const data = await resp.json();
    hideLoading();
    if (data.error) {
      resultEl.innerHTML = '<div style="color:#e8963e;padding:12px;">❌ ' + esc(data.error) + '</div>';
      return;
    }
    const output = data.raw_output || data.output || '(无匹配结果)';
    resultEl.innerHTML = '<div style="background:var(--surface-card);border-radius:8px;padding:16px;border:1px solid var(--border);"><div style="font-weight:600;color:var(--gold);margin-bottom:10px;font-size:14px;">' + (_searchMode === 'ask' ? '💬 AI 回答' : '🔎 语义检索结果') + '</div><div style="white-space:pre-wrap;font-size:13px;line-height:1.7;color:var(--text);">' + esc(output) + '</div></div>';
  } catch (e) {
    hideLoading();
    resultEl.innerHTML = '<div style="color:#e8963e;padding:12px;">❌ 搜索出错: ' + esc(e.message) + '</div>';
  }
}

// ── Link table ──
var _linkPage = 0;
var _linkFiltered = [];

async function refreshLinkTable() {
  const table = document.getElementById('kb-link-table');
  if (!table) return;
  table.innerHTML = '<div style="color:var(--dim);font-size:12px;font-style:italic;padding:6px 0;">加载中...</div>';
  try {
    var resp = await fetch('/api/kb/graph?limit=150');
    var data = await resp.json();
    if (!data.nodes || data.nodes.length === 0 || !data.edges || data.edges.length === 0) {
      table.innerHTML = '<div style="color:var(--dim);font-size:12px;font-style:italic;padding:6px 0;">暂无链接数据</div>';
      return;
    }
    var linkCount = {};
    data.edges.forEach(function(e) { linkCount[e.from] = (linkCount[e.from] || 0) + 1; linkCount[e.to] = (linkCount[e.to] || 0) + 1; });
    var allRows = data.nodes.map(function(n) {
      var cnt = linkCount[n.id] || 0;
      var linked = data.edges.filter(function(e) { return e.from === n.id || e.to === n.id; }).map(function(e) { return e.from === n.id ? e.to : e.from; }).filter(function(id) { return id !== n.id; }).slice(0, 5).join(' · ');
      return { id: n.id, count: cnt, linked: linked };
    });
    _linkFiltered = allRows.filter(function(r) { return r.count > 0; });
    _linkPage = 0;
    renderLinkPage();
  } catch (e) {
    table.innerHTML = '<div style="color:var(--dim);font-size:12px;font-style:italic;padding:6px 0;">加载失败: ' + e.message + '</div>';
  }
}

function renderLinkPage() {
  var table = document.getElementById('kb-link-table');
  if (!table) return;
  var pageSize = 50;
  var total = _linkFiltered.length;
  var totalPages = Math.ceil(total / pageSize);
  var start = _linkPage * pageSize;
  var end = Math.min(start + pageSize, total);
  var pageRows = _linkFiltered.slice(start, end);
  var h = '<div style="margin-bottom:8px;font-size:12px;color:var(--dim);">共 ' + total + ' 个词条有链接关系，第 ' + (_linkPage + 1) + '/' + totalPages + ' 页</div>';
  h += '<table class="link-table"><tr><th>词条</th><th>链接数</th><th>连接到</th></tr>';
  pageRows.forEach(function(r) {
    h += '<tr><td class="article">📄 ' + esc(r.id) + '</td><td class="num">' + r.count + '</td><td class="links">' + (r.linked || '—') + '</td></tr>';
  });
  h += '</table>';
  if (totalPages > 1) {
    h += '<div style="margin-top:10px;text-align:center;font-size:13px;">';
    if (_linkPage > 0) h += '<button onclick="_linkPage--;renderLinkPage()" style="margin-right:8px;padding:4px 12px;background:var(--surface-card);border:1px solid var(--border);border-radius:4px;color:var(--sec);cursor:pointer;">← 上一页</button>';
    h += '<span style="margin:0 8px;color:var(--dim);">' + (_linkPage + 1) + ' / ' + totalPages + '</span>';
    if (_linkPage < totalPages - 1) h += '<button onclick="_linkPage++;renderLinkPage()" style="margin-left:8px;padding:4px 12px;background:var(--surface-card);border:1px solid var(--border);border-radius:4px;color:var(--sec);cursor:pointer;">下一页 →</button>';
    h += '</div>';
  }
  table.innerHTML = h;
}

// ── Nebula (Web UI 引擎：forceAtlas2Based, limit=150, dragNodes=false) ──
let kbNetwork = null;
let _kbFullNodeCount = 0;
let _kbFullNodesMap = {};
let _kbFullEdges = [];
let _kbLoadingFull = false;

async function refreshNebula() {
  var graphEl = document.getElementById('kb-graph');
  if (!graphEl) return;
  graphEl.style.height = '440px';
  if (graphEl.offsetWidth === 0 || graphEl.offsetHeight === 0) {
    requestAnimationFrame(function() { refreshNebula(); });
    return;
  }
  try {
    const resp = await fetch('/api/kb/graph?limit=150');
    const data = await resp.json();
    if (!graphEl) return;
    if (data.error || !data.nodes || data.nodes.length === 0) {
      graphEl.innerHTML = '<div style="color:#888;text-align:center;padding-top:170px;font-size:13px;">✦ 暂无词条</div>';
      return;
    }
    _kbFullNodeCount = data.total_nodes || data.nodes.length;
    const nodes = new vis.DataSet(data.nodes.map(n => ({
      id: n.id, label: n.label, value: n.value || 1,
      color: { background: '#2a82e4', border: '#1a1a3e', highlight: { background: '#d4af37', border: '#fff' } },
      font: { color: '#ccc', size: 12 }, summary: n.summary || '', links: n.links || []
    })));
    const edges = new vis.DataSet(data.edges.map(e => ({
      from: e.from, to: e.to,
      color: { color: '#333366', highlight: '#d4af37', opacity: 0.6 }
    })));
    if (kbNetwork) { kbNetwork.setData({ nodes, edges }); }
    else {
      kbNetwork = new vis.Network(graphEl, { nodes, edges }, {
        physics: { solver: 'forceAtlas2Based', forceAtlas2Based: { gravitationalConstant: -40, centralGravity: 0.005, springLength: 180, springConstant: 0.06 }, stabilization: { iterations: 80 } },
        interaction: { hover: true, zoomView: true, dragView: true, dragNodes: false, selectable: true, selectConnectedEdges: false },
        nodes: { shape: 'dot', size: 12, borderWidth: 1, chosen: false },
        edges: { smooth: false }
      });
      kbNetwork.on('click', function(params) { if (params.nodes.length === 0) kbNetwork.selectNodes([]); });
      kbNetwork.on('hoverNode', function(params) {
        const tip = document.getElementById('kb-tooltip');
        if (!tip || !params.node) return;
        const nd = kbNetwork.body.data.nodes.get(params.node);
        const linksText = (nd.links || []).slice(0, 8).join(' · ') || '无';
        tip.innerHTML = '<div style="font-weight:600;color:#d4af37;margin-bottom:4px;">📄 ' + params.node + '</div><div style="font-size:0.85em;color:#ccc;margin-bottom:6px;line-height:1.4;">' + (nd.summary || '(无摘要)') + '</div><div style="font-size:0.75em;color:#888;">🔗 ' + linksText + '</div><div style="font-size:0.7em;color:#666;margin-top:4px;">双击展开局部网络</div>';
        tip.style.display = 'block';
        var tipRect = tip.getBoundingClientRect();
        var tipW = tipRect.width || 300;
        var tipH = tipRect.height || 180;
        var px = params.event.pageX || 0;
        var py = params.event.pageY || 0;
        var left = px + 15;
        var top = py - 30;
        if (left + tipW > window.innerWidth) left = px - tipW - 15;
        if (top + tipH > window.innerHeight) top = window.innerHeight - tipH - 10;
        if (top < 0) top = 10;
        tip.style.left = left + 'px';
        tip.style.top = top + 'px';
      });
      kbNetwork.on('blurNode', function() { const tip = document.getElementById('kb-tooltip'); if (tip) tip.style.display = 'none'; });
      kbNetwork.on('doubleClick', function(params) {
        if (params.nodes.length === 0) return;
        const nodeId = params.nodes[0];
        if (Object.keys(_kbFullNodesMap).length === 0) {
          showLoading('🌌 展开节点中...');
          fetch('/api/kb/graph?expand=' + encodeURIComponent(nodeId)).then(r => r.json()).then(d => {
            hideLoading();
            if (d.nodes) mergeExpandData(d.nodes, d.edges, nodeId);
          }).catch(e => hideLoading());
          return;
        }
        const localIds = new Set([nodeId]);
        _kbFullEdges.forEach(e => { if (e.from === nodeId) localIds.add(e.to); if (e.to === nodeId) localIds.add(e.from); });
        const localNodes = []; localIds.forEach(id => { if (_kbFullNodesMap[id]) localNodes.push(_kbFullNodesMap[id]); });
        const localEdges = _kbFullEdges.filter(e => localIds.has(e.from) && localIds.has(e.to));
        mergeExpandData(localNodes, localEdges, nodeId);
      });
    }
    kbNetwork.fit({ animation: true });
    if (!_kbLoadingFull && Object.keys(_kbFullNodesMap).length === 0) {
      _kbLoadingFull = true;
      fetch('/api/kb/graph?limit=9999').then(r => r.json()).then(d => {
        if (d.nodes) { _kbFullNodesMap = {}; d.nodes.forEach(n => { _kbFullNodesMap[n.id] = n; }); _kbFullEdges = d.edges || []; }
        _kbLoadingFull = false;
      }).catch(e => { _kbLoadingFull = false; });
    }
  } catch (e) { console.error('Nebula error:', e); }
}

function mergeExpandData(newNodes, newEdges, focusId) {
  if (!kbNetwork) return;
  const moreNodes = new vis.DataSet(newNodes.map(n => ({
    id: n.id, label: n.label, value: n.value || 1,
    color: { background: '#2a82e4', border: '#1a1a3e', highlight: { background: '#d4af37', border: '#fff' } },
    font: { color: '#ccc', size: 12 }, summary: n.summary || '', links: n.links || []
  })));
  const moreEdges = new vis.DataSet(newEdges.map(e => ({
    from: e.from, to: e.to,
    color: { color: '#333366', highlight: '#d4af37', opacity: 0.6 }
  })));
  kbNetwork.body.data.nodes.add(moreNodes.get());
  kbNetwork.body.data.edges.add(moreEdges.get());
  kbNetwork.fit({ animation: true, nodes: [focusId] });
}

// ── Nebula search ──
function doNebulaSearch() {
  var input = document.getElementById('nebula-search-input');
  if (!input) return;
  var q = input.value.trim().toLowerCase();
  if (!q) return;
  if (kbNetwork && kbNetwork.body && kbNetwork.body.data) {
    var nodes = kbNetwork.body.data.nodes.get();
    var matched = nodes.filter(function(n) { return n.label && n.label.toLowerCase().indexOf(q) !== -1; });
    if (matched.length > 0) {
      kbNetwork.selectNodes([matched[0].id]);
      kbNetwork.focus(matched[0].id, { scale: 1.5, animation: true });
      return;
    }
  }
  showLoading('🔍 搜索节点...');
  fetch('/api/kb/graph?limit=9999').then(function(r) { return r.json(); }).then(function(data) {
    hideLoading();
    if (!data.nodes) return;
    var found = data.nodes.filter(function(n) { return n.label && n.label.toLowerCase().indexOf(q) !== -1; });
    if (found.length > 0 && kbNetwork) {
      var moreNodes = new vis.DataSet(found.map(function(n) { return {
        id: n.id, label: n.label, value: n.value || 1,
        color: { background: '#2a82e4', border: '#1a1a3e', highlight: { background: '#d4af37', border: '#fff' } },
        font: { color: '#ccc', size: 12 }, summary: n.summary || '', links: n.links || []
      }; }));
      kbNetwork.body.data.nodes.add(moreNodes.get());
      kbNetwork.selectNodes([found[0].id]);
      kbNetwork.focus(found[0].id, { scale: 1.5, animation: true });
    }
  }).catch(e => hideLoading());
}

// ── Settings ──
async function refreshSettings() {
  var el = document.getElementById('settings-stats');
  if (!el) return;
  try {
    var resp = await fetch('/api/stats');
    var s = await resp.json();
    var chromaInfo = '';
    if (s.chroma_available) {
      var cols = (s.chroma_collections || []).join(', ');
      chromaInfo = '<div style="margin-top:8px;border-top:1px solid var(--border);padding-top:8px;">' +
        '<div style="margin-bottom:2px;">ChromaDB：<code style="color:var(--green);">运行中</code></div>' +
        '<div style="margin-bottom:2px;">索引词条：<code style="color:var(--gold);">' + (s.chroma_count || 0) + '</code></div>' +
        '<div style="font-size:11px;color:var(--dim);">Collections：' + cols + '</div></div>';
    } else {
      chromaInfo = '<div style="margin-top:8px;border-top:1px solid var(--border);padding-top:8px;">' +
        '<div>ChromaDB：<code style="color:var(--orange);">未启用</code></div></div>';
    }
    el.innerHTML =
      '<div style="margin-bottom:2px;">总词条：<code style="color:var(--gold);">' + s.total_count + '</code></div>' +
      '<div style="margin-bottom:2px;">核心词条：<code style="color:var(--green);">' + s.wiki_count + '</code></div>' +
      '<div style="margin-bottom:2px;">归档词条：<code style="color:var(--purple);">' + s.archived_count + '</code></div>' +
      chromaInfo;
  } catch (e) {
    el.innerHTML = '<div style="color:var(--orange);">⚠ API 不可用</div>';
  }
}

// ── Init ──
refreshStats();
refreshNebula();
