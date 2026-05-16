// 知识宇宙 kb.js — 银河星云版
const API = 'http://127.0.0.1:8765';

// ── i18n ──
var _lang = localStorage.getItem('taichu_lang') || 'zh';
var _langPack = {
  zh: {
    'nav.home': '🌌 知识宇宙',
    'nav.upload': '📤 上传',
    'nav.entries': '📄 词条',
    'nav.semantic': '🔍 语义搜索',
    'nav.memory': '🧠 Agent 记忆',
    'nav.aging': '📊 老化列表',
    'nav.settings': '⚙ 设置',
    'common.online': '在线',
    'common.offline': '离线',
    'common.loading': '加载中...',
    'ws.online': '● 在线',
    'ws.offline': '● 离线',
    'stats.total': '总计',
    'stats.wiki': 'Wiki 词条',
    'stats.archive': '归档',
    'stats.core': '核心',
    'stats.archived': '归档',
    'upload.pending': '待编译文件',
    'upload.compile_all': '编译全部',
    'upload.empty': '没有待处理文件',
    'upload.api_unavailable': 'API 不可用',
    'upload.compile_loading': '编译中，请稍候...（可能需要 1-2 分钟）',
    'upload.complete': '完成',
    'upload.failed': '失败',
    'upload.compile_done': '编译完成',
    'upload.compile_fail': '编译失败',
    'upload.compile_error': '编译 API 错误',
    'upload.drop': '拖拽文件到这里上传\n或点击选择文件',
    'entries.title': '词条',
    'entries.count': '共',
    'entries.page': '第',
    'entries.page_total': '页',
    'entries.prev': '‹ 上一页',
    'entries.next': '下一页 ›',
    'entries.no_match': '无匹配词条',
    'entries.load_fail': '无法加载词条列表',
    'entries.search_placeholder': '搜索词条...',
    'entries.subtitle': '全部词条列表',
    'search.title': '语义搜索',
    'search.placeholder': '输入搜索词或问题...',
    'search.semantic': '语义检索',
    'search.ask': 'AI 问答',
    'search.btn': '搜索',
    'search.running': '搜索中...',
    'search.no_query': '请输入搜索词或问题',
    'search.api_error': '搜索 API 不可用',
    'settings.knowledge': '知识库',
    'settings.database': '数据库',
    'settings.model': '模型',
    'settings.language': '语言',
    'settings.stats': '统计',
    'settings.connection': '连接',
    'settings.runtime': '指标',
    'settings.graphics': '渲染',
    'settings.kb_path': '知识库路径',
    'settings.store_path': '存储路径',
    'settings.api_service': 'API 服务',
    'settings.api_conn': 'API 服务',
    'settings.ws_conn': 'WebSocket',
    'settings.db_index': '数据库索引',
    'settings.chroma_status': 'ChromaDB',
    'settings.vector_count': '向量索引数',
    'settings.index_collections': '索引集合',
    'settings.ai_model': 'AI 模型',
    'settings.lang_title': '语言',
    'settings.ui_lang': '界面语言',
    'settings.file_stats': '文件统计',
    'settings.conn_status': '连接状态',
    'settings.runtime_metrics': '运行指标',
    'settings.render_quality': '渲染画质',
    'settings.search_engine': '搜索引擎',
    'model.current': '当前模型',
    'model.switch': '切换模型',
    'model.select_provider': '— 选择提供商 —',
    'model.switch_to': '切换到',
    'model.base_url': 'Base URL',
    'model.api_endpoint': 'API 入口',
    'model.api_key': 'API Key（留空使用当前）',
    'model.confirm_switch': '确认切换',
    'model.cancel': '取消',
    'common.confirm': '确认',
    'model.switching': '切换中...',
    'model.no_provider': '请选择提供商',
    'model.req_fail': '请求失败',
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
    'gfx.updated': '已更新',
    'gfx.webgl_unavailable': '当前环境不支持 WebGL',
    'panel.title': '知识节点',
    'panel.title_en': 'Node Insight',
    'panel.placeholder': '悬停或点击节点查看详情',
    'panel.neighbors': '关联节点',
    'panel.cluster': '集群',
    'panel.gravity': '重力',
    'panel.not_found': '未找到节点',
    'nebula.search_placeholder': '输入节点名称...',
    'nebula.goto': '跳转',
    'nebula.mode_3d': '3D 全息模式',
    'delete.confirm': '确定删除',
    'delete.success': '已删除',
    'delete.fail': '删除失败',
    'result.update': '已更新',
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
  },
  en: {
    'nav.home': '🌌 Knowledge Universe',
    'nav.upload': '📤 Upload',
    'nav.entries': '📄 Entries',
    'nav.semantic': '🔍 Semantic',
    'nav.memory': '🧠 Memory',
    'nav.aging': '📊 Aging',
    'nav.settings': '⚙ Settings',
    'common.online': 'Online',
    'common.offline': 'Offline',
    'common.loading': 'Loading...',
    'ws.online': '● Online',
    'ws.offline': '● Offline',
    'stats.total': 'Total',
    'stats.wiki': 'Wiki Articles',
    'stats.archive': 'Archived',
    'stats.core': 'Core',
    'stats.archived': 'Archived',
    'upload.pending': 'Pending Files',
    'upload.compile_all': 'Compile All',
    'upload.empty': 'No pending files',
    'upload.api_unavailable': 'API unavailable',
    'upload.compile_loading': 'Compiling, please wait... (1-2 min)',
    'upload.complete': 'Complete',
    'upload.failed': 'Failed',
    'upload.compile_done': 'Compile complete',
    'upload.compile_fail': 'Compile failed',
    'upload.compile_error': 'Compile API error',
    'upload.drop': 'Drop files here to upload\nor click to select',
    'entries.title': 'Entries',
    'entries.count': 'Total',
    'entries.page': 'Page',
    'entries.page_total': '',
    'entries.prev': '‹ Prev',
    'entries.next': 'Next ›',
    'entries.no_match': 'No matching entries',
    'entries.load_fail': 'Cannot load entries',
    'entries.search_placeholder': 'Search entries...',
    'entries.subtitle': 'All entries',
    'search.title': 'Semantic Search',
    'search.placeholder': 'Enter search term or question...',
    'search.semantic': 'Semantic',
    'search.ask': 'AI Q&A',
    'search.btn': 'Search',
    'search.running': 'Searching...',
    'search.no_query': 'Please enter a search term',
    'search.api_error': 'Search API unavailable',
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
    'settings.api_conn': 'API Service',
    'settings.ws_conn': 'WebSocket',
    'settings.db_index': 'Database Index',
    'settings.chroma_status': 'ChromaDB',
    'settings.vector_count': 'Vector Count',
    'settings.index_collections': 'Collections',
    'settings.ai_model': 'AI Model',
    'settings.lang_title': 'Language',
    'settings.ui_lang': 'Interface Language',
    'settings.file_stats': 'File Statistics',
    'settings.conn_status': 'Connection Status',
    'settings.runtime_metrics': 'Runtime Metrics',
    'settings.render_quality': 'Render Quality',
    'settings.search_engine': 'Search Engine',
    'model.current': 'Current Model',
    'model.switch': 'Switch Model',
    'model.select_provider': '— Select Provider —',
    'model.switch_to': 'Switch to',
    'model.base_url': 'Base URL',
    'model.api_endpoint': 'API Endpoint',
    'model.api_key': 'API Key (leave empty)',
    'model.confirm_switch': 'Confirm',
    'model.cancel': 'Cancel',
    'common.confirm': 'Confirm',
    'model.switching': 'Switching...',
    'model.no_provider': 'Please select a provider',
    'model.req_fail': 'Request failed',
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
    'gfx.hint_renderer': 'GPU uses hardware acceleration',
    'gfx.hint_view': '3D requires GPU mode',
    'gfx.hint_limit': 'Higher = more resource intensive',
    'gfx.updated': 'Updated',
    'gfx.webgl_unavailable': 'WebGL not available',
    'panel.title': '知识节点',
    'panel.title_en': 'Node Insight',
    'panel.placeholder': 'Hover or click a node for details',
    'panel.neighbors': 'Neighbors',
    'panel.cluster': 'Cluster',
    'panel.gravity': 'Gravity',
    'panel.not_found': 'Node not found',
    'nebula.search_placeholder': 'Enter node name...',
    'nebula.goto': 'Go',
    'nebula.mode_3d': '3D Hologram',
    'delete.confirm': 'Delete',
    'delete.success': 'Deleted',
    'delete.fail': 'Delete failed',
    'result.update': 'Updated',
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
  }
};
function __(k) { return (_langPack[_lang] || _langPack.zh)[k] || k; }
function updateLangUI(){
  // Panel title
  var el=document.getElementById('panel-title');
  if(el){el.textContent=_lang==='en'?'Node Insight':'知识节点';}
  // Update data-i18n elements
  document.querySelectorAll('[data-i18n]').forEach(function(el){
    var key=el.dataset.i18n;
    el.textContent=__(key);
  });
  // Update data-i18n-placeholder elements
  document.querySelectorAll('[data-i18n-placeholder]').forEach(function(el){
    el.placeholder=__(el.dataset.i18nPlaceholder);
  });
}

const tabs = document.querySelectorAll('.nav-item');
var _memoryTimer = null, _agingTimer = null;
tabs.forEach(function(tab){
  tab.addEventListener('click',function(){
    tabs.forEach(function(t){t.classList.remove('active');});
    tab.classList.add('active');
    const tabId = tab.dataset.tab;
    document.querySelectorAll('#content-area > div').forEach(function(d){d.style.display='none';});
    document.getElementById('tab-'+tabId).style.display='block';
    if(tabId==='home'){setTimeout(function(){resizeCanvas2D();resizeThree();}, 50);}
    if(tabId==='upload'){refreshPending();refreshUploadStats();}
    if(tabId==='entries'){loadEntries();}
    if(tabId==='settings'){refreshSettings();}
    // Dashboard auto-refresh
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

let apiOnline = false;
function checkAPIBadge(){
  fetch(API+'/health').then(function(r){return r.json();}).then(function(d){
    apiOnline = d.status==='ok';
    document.getElementById('api-status').className = apiOnline ? 'online' : 'err';
    document.getElementById('api-status').innerText = apiOnline ? __('ws.online') : __('ws.offline');
    document.getElementById('set-api-status').innerHTML = apiOnline ? '<span class="ok">'+__('ws.online')+'</span>' : '<span class="err">'+__('ws.offline')+'</span>';
  }).catch(function(e){
    console.warn('[health] API not reachable:',e);
    apiOnline = false;
    document.getElementById('api-status').className = 'err';
    document.getElementById('api-status').innerText = __('ws.offline');
    document.getElementById('set-api-status').innerHTML = '<span class="err">'+__('ws.offline')+'</span>';
  });
}

const uploadArea = document.getElementById('upload-area');
const fileList = document.getElementById('file-list');

// 支持的文件类型（与后端 SUPPORTED_EXT 同步）
const SUPPORTED_EXT = [
  'txt','md','markdown','json','csv','xml',
  'py','js','ts','rs','c','cpp','h','java','go','rb','sh','yaml','toml',
  'zip','tar','gz','7z','rar',
  'pdf','doc','docx','xls','xlsx','ppt','pptx',
  'png','jpg','jpeg','webp','gif','bmp','svg',
  'wasm','html','htm','rtf','epub'
];
const ACCEPT_STR = SUPPORTED_EXT.map(function(e){return '.'+e;}).join(',');

function handleFiles(files){
  for(let i=0;i<files.length;i++){
    const f=files[i];
    const ext=f.name.split('.').pop().toLowerCase();
    if(SUPPORTED_EXT.indexOf(ext)===-1){
      showResult('❌ 不支持的文件类型: '+f.name,'err');
      continue;
    }
    const li=document.createElement('li');
    li.textContent=f.name+' ('+(f.size/1024).toFixed(1)+' KB)';
    fileList.appendChild(li);
    uploadFileToAPI(f);
  }
}

// ── Tauri IPC 辅助 ──
function tauriInvoke(cmd, args){
  try {
    if(window.__TAURI__ && window.__TAURI__.core) {
      return window.__TAURI__.core.invoke(cmd, args||{});
    }
  } catch(e) {
    console.warn('[tauriInvoke] invoke failed:', e);
  }
  return Promise.reject(new Error('Tauri IPC not available'));
}

// ── 上传 ──
uploadArea.addEventListener('dragover', function(e){e.preventDefault();uploadArea.classList.add('dragover');});
uploadArea.addEventListener('dragleave', function(e){e.preventDefault();uploadArea.classList.remove('dragover');});
uploadArea.addEventListener('drop', function(e){e.preventDefault();uploadArea.classList.remove('dragover');handleFiles(e.dataTransfer.files);});
uploadArea.addEventListener('click', function(){
  // Tauri 环境使用 IPC dialog（通过文件输入回退）
  const input=document.createElement('input');input.type='file';input.multiple=true;
  input.accept=ACCEPT_STR;
  input.onchange=function(){handleFiles(input.files);};
  input.click();
});

// Tauri 原生拖拽事件（替代 HTML5 drop，后者在 Tauri 中被拦截）
function setupTauriDragDrop(){
  if(!window.__TAURI__||!window.__TAURI__.event) return;
  window.__TAURI__.event.listen('tauri-drag-enter', function(){uploadArea.classList.add('dragover');});
  window.__TAURI__.event.listen('tauri-drag-leave', function(){uploadArea.classList.remove('dragover');});
  window.__TAURI__.event.listen('tauri-drag-drop', function(ev){
    uploadArea.classList.remove('dragover');
    var paths=ev.payload||[];
    paths.forEach(function(p){uploadFileToAPI_path(p);});
  });
}
setupTauriDragDrop();

function uploadFileToAPI(file){
  // Tauri 环境：通过 IPC 发送 base64 数据
  if(window.__TAURI__){
    showLoading('📤 上传 '+file.name+'...');
    var reader=new FileReader();
    reader.onload=function(){
      var base64=reader.result.split(',')[1];
      tauriInvoke('upload_file_data',{file_name:file.name,data_base64:base64}).then(function(d){
        hideLoading();
        if(d&&d.ok){refreshPending();showResult('✅ '+(d.md_count>0?d.md_count+'个.md已发布 ':'')+(d.other_count>0?d.other_count+'个文件待编译':''),'ok');}
        else{showResult('❌ 上传失败: '+(d&&d.note||'未知错误'),'err');}
      }).catch(function(e){
        console.warn('[upload] IPC 失败，降级到 HTTP:', e);
        hideLoading();
        // 降级到 HTTP multipart 上传
        _httpUpload(file);
      });
    };
    reader.onerror=function(){hideLoading();showResult('❌ 文件读取失败','err');};
    reader.readAsDataURL(file);
    return;
  }
  // 浏览器回退：HTTP multipart 上传
  _httpUpload(file);
}

function _httpUpload(file){
  showLoading('📤 上传 '+file.name+'...');
  const formData=new FormData();formData.append('files',file);
  fetch(API+'/upload',{method:'POST',body:formData}).then(function(r){return r.json();}).then(function(d){
    hideLoading();
    if(d.ok){
      refreshPending();
      const n=d.md_count||0;const o=d.other_count||0;
      showResult('✅ '+(n>0?n+'个.md已发布 ':'')+(o>0?o+'个文件待编译':''),'ok');
    }else{showResult('❌ 上传失败: '+(d.error||'未知错误'),'err');}
  }).catch(function(e){hideLoading();showResult('❌ 上传请求失败','err');console.error('[httpUpload] error:', e);});
}

// Tauri 原生拖拽：直接通过路径上传
function uploadFileToAPI_path(filePath){
  showLoading('📤 上传文件...');
  // Tauri IPC 上传，失败则降级到 HTTP
  tryUploadIPC('upload_file', {path: filePath}, function(d){
    hideLoading();
    if(d&&d.ok){refreshPending();showResult('✅ 上传成功'+(d.md_count>0?' ('+d.md_count+'个.md)':'')+(d.other_count>0?' ('+d.other_count+'个待编译)':''),'ok');}
    else{showResult('❌ 上传失败: '+(d&&d.note||'未知错误'),'err');}
  }, function(){
    hideLoading();
    showResult('❌ 无法上传文件路径（仅 Tauri 桌面端支持拖拽上传）','err');
  });
}

function tryUploadIPC(cmd, args, onOk, onFallback){
  if(!window.__TAURI__){onFallback();return;}
  tauriInvoke(cmd, args).then(function(d){
    if(onOk) onOk(d);
  }).catch(function(e){
    console.warn('[upload] IPC '+cmd+' failed:', e);
    if(onFallback) onFallback(e);
  });
}

function refreshPending(){const list=document.getElementById('pending-list');const badge=document.getElementById('pending-badge');
  fetch(API+'/api/kb/pending').then(function(r){return r.json();}).then(function(d){const files=d.pending||[];badge.innerText='('+files.length+(_lang==='zh'?' 个)':')');
    if(files.length===0){list.innerHTML='<li style="color:rgba(255,255,255,0.3);font-size:12px;padding:8px 10px;">✦ '+__('upload.empty')+'</li>';return;}
    list.innerHTML='';files.forEach(function(f){const li=document.createElement('li');li.className='pending-item';
      const sizeStr=f.size>1024?(f.size/1024).toFixed(1)+'KB':f.size+'B';li.innerHTML='<span class="pending-name">'+escHtml(f.name)+'</span><span class="pending-size">'+sizeStr+'</span>';
      const delBtn=document.createElement('button');delBtn.className='del-btn';delBtn.textContent='✕';delBtn.dataset.filename=f.name;
      delBtn.addEventListener('click',function(){deletePending(this.dataset.filename);});li.appendChild(delBtn);list.appendChild(li);});
  }).catch(function(){list.innerHTML='<li style="color:rgba(255,255,255,0.3);font-size:12px;padding:8px 10px;">⚠ '+__('upload.api_unavailable')+'</li>';});}
function deletePending(filename){
  if(!confirm(__('delete.confirm')+'「'+filename+'」?'))return;
  fetch(API+'/api/kb/pending/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({filename:filename})}).then(function(r){return r.json();}).then(function(d){
    refreshPending();showResult('🗑 '+__('delete.success')+': '+filename,'ok');
  }).catch(function(e){showResult('❌ '+__('delete.fail'),'err');console.warn('[deletePending] error:',e);});
}
function triggerCompile(){const btn=document.getElementById('compile-btn');btn.disabled=true;btn.innerText='⏳ '+__('common.loading');showLoading('⚡ '+__('upload.compile_loading'));
  fetch(API+'/api/kb/compile',{method:'POST'}).then(function(r){return r.json();}).then(function(d){btn.disabled=false;hideLoading();
    if(d.ok){btn.innerText='✅ '+__('upload.complete')+' ('+(d.converted||0)+(_lang==='zh'?' 个)':')');setTimeout(function(){btn.innerText='⚡ '+__('upload.compile_all');},2000);refreshPending();showResult('✅ '+__('upload.compile_done')+': '+(d.converted||0)+(_lang==='zh'?' 个文件':' files'),'ok');}
    else{btn.innerText='❌ '+__('upload.failed');setTimeout(function(){btn.innerText='⚡ '+__('upload.compile_all');},2000);showResult('❌ '+__('upload.compile_fail'),'err');}
  }).catch(function(){btn.disabled=false;hideLoading();btn.innerText='❌ '+__('upload.compile_error');setTimeout(function(){btn.innerText='⚡ '+__('upload.compile_all');},2000);showResult('❌ '+__('upload.compile_error'),'err');});}

let allEntries=[];let entriesPage=0;const entriesPageSize=20;
let _confidenceScores = [];

function loadEntries(){const list=document.getElementById('entries-list');const countEl=document.getElementById('entries-count');
  fetch(API+'/api/stats').then(function(r){return r.json();}).then(function(d){allEntries=(d.wiki_articles||[]).filter(function(n){return !n.startsWith('_');});
    const core=allEntries.filter(function(n){return !n.startsWith('archive-');});const archived=allEntries.filter(function(n){return n.startsWith('archive-');});
    countEl.innerText=__('entries.count')+' '+(d.wiki_count||0)+(_lang==='zh'?' 个词条':' entries')+' ('+core.length+' '+__('stats.core')+' + '+archived.length+' '+__('stats.archived')+')';entriesPage=0;renderEntriesPage();
    // Load confidence scores
    fetch(API+'/api/kb/confidence').then(function(r){return r.json();}).then(function(cd){_confidenceScores=cd.scores||[];renderEntriesPage();}).catch(function(){});
  }).catch(function(){countEl.innerText=__('upload.api_unavailable');list.innerHTML='<li style="color:rgba(255,255,255,0.3);padding:8px;">'+__('entries.load_fail')+'</li>';});}
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

function renderEntriesPage(){const list=document.getElementById('entries-list');const start=entriesPage*entriesPageSize;const page=allEntries.slice(start,start+entriesPageSize);
  list.innerHTML='';page.forEach(function(name){const li=document.createElement('li');li.innerHTML=getConfBadge(name)+escHtml(name.replace(/^archive-/i,'').replace(/\.md$/,''));if(name.startsWith('archive-'))li.style.opacity=0.5;list.appendChild(li);});
  const totalPages=Math.ceil(allEntries.length/entriesPageSize);const nav=document.createElement('li');
  nav.style.cssText='border:none !important;padding:8px 0;text-align:center;font-size:12px;color:rgba(255,255,255,0.4);';
  const prevBtn=entriesPage>0?'<span class="page-btn" data-dir="prev" style="cursor:pointer;color:#7dd3fc;margin:0 8px;">'+__('entries.prev')+'</span>':'';
  const nextBtn=entriesPage<totalPages-1?'<span class="page-btn" data-dir="next" style="cursor:pointer;color:#7dd3fc;margin:0 8px;">'+__('entries.next')+'</span>':'';
  nav.innerHTML=prevBtn+__('entries.page')+' '+(entriesPage+1)+'/'+totalPages+' '+__('entries.page_total')+nextBtn;list.appendChild(nav);}
function filterEntries(){const q=document.getElementById('entries-search').value.trim().toLowerCase();if(!q){renderEntriesPage();return;}
  const list=document.getElementById('entries-list');const matched=allEntries.filter(function(n){return n.toLowerCase().includes(q);});
  list.innerHTML='';if(matched.length===0){list.innerHTML='<li style="color:rgba(255,255,255,0.3);padding:8px;">'+__('entries.no_match')+'</li>';return;}
  matched.forEach(function(name){const li=document.createElement('li');li.innerHTML=getConfBadge(name)+escHtml(name.replace(/^archive-/i,'').replace(/\.md$/,''));if(name.startsWith('archive-'))li.style.opacity=0.5;list.appendChild(li);});}

let searchMode='search';
function setSearchMode(mode){searchMode=mode;['mode-search','mode-ask'].forEach(function(id){const el=document.getElementById(id);if(!el)return;el.className=(mode==='search'&&id==='mode-search')||(mode==='ask'&&id==='mode-ask')?'active':'';});}
document.getElementById('semantic-search').addEventListener('click',async function(){const query=document.getElementById('semantic-query').value.trim();const results=document.getElementById('semantic-results');
  if(!query){results.innerHTML='<span style="color:rgba(255,255,255,0.4);font-style:italic;">'+__('search.no_query')+'</span>';return;}
  results.innerHTML='<span style="color:rgba(255,255,255,0.4);">⏳ '+__('search.running')+'</span>';
  try{const endpoint=searchMode==='ask'?'ask':'search';const r=await fetch(API+'/api/kb/'+endpoint+'?q='+encodeURIComponent(query));const d=await r.json();
    if(d.error){results.innerHTML='<span style="color:#f87171;">❌ '+escHtml(d.error)+'</span>';return;}
    const output=d.raw_output||d.output||'(无匹配结果)';const label=searchMode==='ask'?'💬 '+__('search.ask'):'🔎 '+__('search.semantic');
    results.innerHTML='<div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:16px;border:1px solid rgba(255,255,255,0.06);"><div style="font-weight:600;color:#d4af37;margin-bottom:10px;font-size:14px;">'+label+'</div><div style="white-space:pre-wrap;font-size:13px;line-height:1.7;color:rgba(255,255,255,0.85);">'+escHtml(output)+'</div></div>';
  }catch(e){results.innerHTML='<span style="color:#f87171;">❌ '+__('search.api_error')+'</span>';}});
document.getElementById('semantic-query').addEventListener('keydown',function(e){if(e.key==='Enter'){document.getElementById('semantic-search').click();}});

function initSettingsSidebar(){
  var items=document.querySelectorAll('#tab-settings .settings-sidebar-item');
  items.forEach(function(item){
    item.addEventListener('click',function(){
      items.forEach(function(i){i.classList.remove('active');});
      item.classList.add('active');
      var panelId=item.dataset.settingsPanel;
      document.querySelectorAll('#tab-settings .settings-panel').forEach(function(p){p.classList.remove('active');});
      var panel=document.getElementById('settings-'+panelId);
      if(panel)panel.classList.add('active');
      if(panelId==='graphics')renderGfxPanel();
      var mf=document.getElementById('model-switch-form');
      if(mf)mf.style.display='none';
      var ms=document.getElementById('model-provider-select');
      if(ms)ms.value='';
    });
  });
}

function loadGfxSettings(){
  _gfxSettings={};
  var keys=['renderer','view_mode','layout_mode','node_limit','rotation_speed','node_size'];
  keys.forEach(function(k){
    var v=localStorage.getItem('taichu_gfx_'+k);
    if(v!==null)_gfxSettings[k]=v;
  });
  if(!_gfxSettings.renderer)_gfxSettings.renderer='cpu';
  if(!_gfxSettings.view_mode)_gfxSettings.view_mode='2d';
  if(!_gfxSettings.layout_mode||_gfxSettings.layout_mode==='circle')_gfxSettings.layout_mode='spiral';
  if(!_gfxSettings.node_limit)_gfxSettings.node_limit='700';
  if(!_gfxSettings.rotation_speed)_gfxSettings.rotation_speed='normal';
  if(!_gfxSettings.node_size)_gfxSettings.node_size='medium';
  applyGfxToNebula();
}
function applyGfxToNebula(){
  _gfxNodeLimit=parseInt(_gfxSettings.node_limit,10)||700;
  var speedMap={off:0,slow:0.5,normal:1,fast:2};
  _gfxRotationSpeed=speedMap[_gfxSettings.rotation_speed]||1;
  var sizeMap={small:0.6,medium:1,large:1.6};
  _gfxNodeSizeScale=sizeMap[_gfxSettings.node_size]||1;
  _gfxLayoutMode=_gfxSettings.layout_mode||'spiral';
  // Sync to existing globals
  NODE_COUNT=_gfxNodeLimit;
  if(_gfxSettings.view_mode==='3d'&&CAN_3D)USE_3D=true;
  else USE_3D=false;
}
function saveGfxSetting(key,value){
  _gfxSettings[key]=value;
  localStorage.setItem('taichu_gfx_'+key,value);
  applyGfxToNebula();
}
function renderGfxPanel(){
  var panel=document.getElementById('gfx-panel');
  if(!panel)return;
  var s=_gfxSettings;
  var rows=[
    {label:__('gfx.renderer'),key:'renderer',opts:[{v:'cpu',t:__('gfx.cpu')},{v:'gpu',t:__('gfx.gpu')}],hint:__('gfx.hint_renderer')},
    {label:__('gfx.view_mode'),key:'view_mode',opts:[{v:'2d',t:__('gfx._2d')},{v:'3d',t:__('gfx._3d')}],hint:__('gfx.hint_view')},
    {label:__('gfx.layout_mode'),key:'layout_mode',opts:[{v:'spiral',t:__('gfx.spiral')}],hint:''},
    {label:__('gfx.node_limit'),key:'node_limit',opts:[{v:'50',t:'50'},{v:'150',t:'150'},{v:'300',t:'300'},{v:'500',t:'500'},{v:'700',t:'700'},{v:'1000',t:'1000'}],hint:__('gfx.hint_limit')},
    {label:__('gfx.rotation_speed'),key:'rotation_speed',opts:[{v:'off',t:__('gfx.off')},{v:'slow',t:__('gfx.slow')},{v:'normal',t:__('gfx.normal')},{v:'fast',t:__('gfx.fast')}],hint:''},
    {label:__('gfx.node_size'),key:'node_size',opts:[{v:'small',t:__('gfx.small')},{v:'medium',t:__('gfx.medium')},{v:'large',t:__('gfx.large')}],hint:''}
  ];
  var html='';
  for(var i=0;i<rows.length;i++){
    var r=rows[i];
    var selected=s[r.key]||'';
    html+='<div class="gfx-row">';
    html+='  <div><div class="gfx-label">'+r.label+'</div>';
    if(r.hint)html+='  <div class="gfx-hint">'+r.hint+'</div>';
    html+='  </div>';
    html+='  <div class="gfx-control"><select data-gfx-key="'+r.key+'">';
    for(var j=0;j<r.opts.length;j++){
      var o=r.opts[j];
      html+='<option value="'+o.v+'"'+(o.v===selected?' selected':'')+'>'+o.t+'</option>';
    }
    html+='</select></div></div>';
  }
  html+='<div style="margin-top:12px;text-align:center;"><button id="gfx-confirm-btn" style="background:var(--gold);color:#050816;border:none;padding:8px 24px;border-radius:4px;cursor:pointer;font-weight:600;font-size:13px;">'+__('common.confirm')+'</button></div>';
  panel.innerHTML=html;
  panel.querySelectorAll('select[data-gfx-key]').forEach(function(sel){
    sel.addEventListener('change',function(){
      var key=this.dataset.gfxKey;
      var val=this.value;
      if(key==='view_mode'&&val==='3d'&&!CAN_3D){
        showResult('⚠ '+__('gfx.webgl_unavailable'),'err');
        this.value=_gfxSettings[key];
        return;
      }
      localStorage.setItem('taichu_gfx_'+key,val);
    });
  });
  document.getElementById('gfx-confirm-btn').addEventListener('click',function(){
    panel.querySelectorAll('select[data-gfx-key]').forEach(function(sel){
      _gfxSettings[sel.dataset.gfxKey]=sel.value;
    });
    applyGfxToNebula();
    if(_gfxSettings.view_mode==='3d'&&CAN_3D){
      USE_3D=true;document.getElementById('canvas2d').style.display='none';document.getElementById('canvas3d').style.display='block';
      document.getElementById('modeText').innerText='3D';initScene3D();
    }else{
      USE_3D=false;document.getElementById('canvas2d').style.display='block';document.getElementById('canvas3d').style.display='none';
      document.getElementById('modeText').innerText='2D';
    }
    var c=parseInt(_gfxSettings.node_limit)||700;
    NODE_COUNT=Math.max(50,Math.min(5000,c));
    createNodeData(NODE_COUNT);initNodePositions();
    document.getElementById('nodeCountText').innerText=NODE_COUNT;
    showResult('✔ '+__('gfx.updated'),'ok');
  });
}

function refreshSettings(){
  initSettingsSidebar();
  loadGfxSettings();
  fetch(API+'/api/stats').then(function(r){return r.json();}).then(function(d){
    document.getElementById('set-wiki-count').innerText=d.wiki_count||'--';
    document.getElementById('set-archive-count').innerText=d.archived_count||'--';
    document.getElementById('set-total-count').innerText=d.total_count||'--';
    var chromaEl=document.getElementById('set-chroma-status');
    if(chromaEl)chromaEl.innerHTML=d.chroma_available?'<span class="ok">● '+__('common.online')+'</span>':'<span class="err">● '+__('common.offline')+'</span>';
    var ccEl=document.getElementById('set-chroma-count');
    if(ccEl)ccEl.innerText=d.chroma_count||0;
    var colsEl=document.getElementById('set-chroma-cols');
    if(colsEl)colsEl.innerText=(d.chroma_collections||['taichu_memory']).join(', ');
  }).catch(function(e){console.warn('[refreshSettings] API error:',e);});
  // Connection status
  var apiStatusEl=document.getElementById('set-api-status');
  var wsStatusEl=document.getElementById('set-ws-status');
  if(apiStatusEl)apiStatusEl.innerHTML=apiOnline?'<span class="ok">'+__('ws.online')+'</span>':'<span class="err">'+__('ws.offline')+'</span>';
  if(wsStatusEl)wsStatusEl.innerHTML=(ws&&ws.readyState===WebSocket.OPEN)?'<span class="ok">'+__('ws.online')+'</span>':'<span class="err">'+__('ws.offline')+'</span>';
  // Runtime metrics
  var metricsEl=document.getElementById('settings-metrics');
  if(metricsEl){
    fetch(API+'/api/metrics').then(function(r){return r.json();}).then(function(metrics){
      if(metrics.graph){
        metricsEl.innerHTML='<table style="width:100%;font-size:12px;border-collapse:collapse;">'+
          '<tr><td style="color:var(--dim);padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.06);">检索次数</td><td style="text-align:right;padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.06);">'+(metrics.retrieval.queries||0)+'</td></tr>'+
          '<tr><td style="color:var(--dim);padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.06);">平均耗时</td><td style="text-align:right;padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.06);">'+(metrics.retrieval.avg_latency_ms||0)+'ms</td></tr>'+
          '<tr><td style="color:var(--dim);padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.06);">图谱节点</td><td style="text-align:right;padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.06);">'+(metrics.graph.nodes||'--')+'</td></tr>'+
          '<tr><td style="color:var(--dim);padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.06);">孤岛节点</td><td style="text-align:right;padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.06);">'+(metrics.graph.orphan_nodes||'--')+'</td></tr>'+
          '<tr><td style="color:var(--dim);padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.06);">平均邻居</td><td style="text-align:right;padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.06);">'+(metrics.graph.avg_neighbors||'--')+'</td></tr>'+
          '</table>'+
          '<div style="margin-top:10px;"><button onclick="runPipelineTrace()" style="background:var(--gold);color:#050816;border:none;padding:5px 14px;border-radius:4px;cursor:pointer;font-size:12px;font-weight:600;">🔍 运行 Pipeline</button></div>'+
          '<div id="pipeline-trace" style="margin-top:6px;font-size:11px;color:var(--sec);"></div>';
      }else{
        metricsEl.innerHTML='<div style="color:var(--dim);font-style:italic;font-size:12px;">指标不可用</div>';
      }
    }).catch(function(){
      metricsEl.innerHTML='<div style="color:var(--dim);font-style:italic;font-size:12px;">指标加载失败</div>';
    });
  }
  // Model panel
  refreshModelPanel();
  // Render gfx panel if active
  if(document.getElementById('settings-graphics').classList.contains('active'))renderGfxPanel();
  // Language select
  var langSel=document.getElementById('lang-select');
  var langBtn=document.getElementById('lang-confirm');
  if(langSel){langSel.value=_lang;}
  if(langBtn){
    langBtn.onclick=function(){
      _lang=langSel.value;
      localStorage.setItem('taichu_lang',_lang);
      updateLangUI();
    };
  }
}
function runPipelineTrace(){
  var traceEl=document.getElementById('pipeline-trace');
  if(!traceEl)return;
  traceEl.innerHTML='⏳ '+__('common.loading');
  fetch(API+'/api/pipeline/trace?q='+encodeURIComponent('transformer attention')).then(function(r){return r.json();}).then(function(d){
    if(d.error){traceEl.innerHTML='<span style="color:var(--orange);">'+escHtml(d.error)+'</span>';return;}
    var stages=[
      ['query_parser','解析查询'],
      ['vector_search','向量搜索'],
      ['graph_expand','图谱扩展'],
      ['ontology_filter','本体过滤'],
      ['rerank','重排序'],
      ['context_builder','上下文组装']
    ];
    var html='<table style="width:100%;font-size:11px;border-collapse:collapse;">';
    for(var i=0;i<stages.length;i++){
      var s=stages[i];
      var ms=d.timers[s[0]]||0;
      var color=ms>1000?'var(--orange)':ms>200?'var(--gold)':'var(--green)';
      var badge=ms>1000?' ✗':ms>200?' ⚠':' ✓';
      html+='<tr><td style="color:var(--dim);padding:2px 0;border-bottom:1px solid rgba(255,255,255,0.04);">'+s[1]+'</td><td style="text-align:right;color:'+color+';padding:2px 0;border-bottom:1px solid rgba(255,255,255,0.04);">'+ms+'ms'+badge+'</td></tr>';
    }
    html+='<tr><td style="border-top:1px solid rgba(255,255,255,0.06);padding:2px 0;font-weight:600;color:var(--text);">总计</td><td style="border-top:1px solid rgba(255,255,255,0.06);text-align:right;font-weight:600;color:var(--text);">'+d.total_ms+'ms</td></tr>';
    html+='<tr><td style="color:var(--dim);padding:2px 0;">结果数</td><td style="text-align:right;color:var(--sec);padding:2px 0;">'+d.result_count+'</td></tr>';
    if(d.graph_nodes_expanded>0)html+='<tr><td style="color:var(--dim);padding:2px 0;">图谱扩展</td><td style="text-align:right;color:var(--sec);padding:2px 0;">'+d.graph_nodes_expanded+' 节点</td></tr>';
    html+='</table>';
    html+='<div style="margin-top:6px;font-size:10px;color:var(--dim);">参考：<span style="color:var(--green);">✓ &lt;200ms</span> · <span style="color:var(--gold);">⚠ 200~1000ms</span> · <span style="color:var(--orange);">✗ &gt;1s</span></div>';
    traceEl.innerHTML=html;
  }).catch(function(){traceEl.innerHTML='<span style="color:var(--orange);">❌ Pipeline API 不可用</span>';});
}
function refreshUploadStats(){
  fetch(API+'/api/stats').then(function(r){return r.json();}).then(function(d){
    var te=document.getElementById('upload-total-count');
    var we=document.getElementById('upload-wiki-count');
    var ae=document.getElementById('upload-archive-count');
    if(te)te.innerText=d.total_count||'--';
    if(we)we.innerText=d.wiki_count||'--';
    if(ae)ae.innerText=d.archived_count||'--';
  }).catch(function(){});
}
var _providersData=[];

function refreshModelPanel(){
  var panel=document.getElementById('model-panel');
  if(!panel)return;
  fetch(API+'/api/models').then(function(r){return r.json();}).then(function(d){
    _providersData=d.providers||[];
    var html='<div style="margin-bottom:12px;font-weight:600;color:var(--text);">'+__('model.current')+'</div>';
    var roles={compile:'编译/推理',query:'快速问答',reasoning:'复杂推理',embedding:'向量嵌入',vision:'视觉分析'};
    var roleOrder=['compile','query','reasoning','embedding','vision'];
    for(var i=0;i<roleOrder.length;i++){
      var role=roleOrder[i];
      var c=d.current[role];
      if(!c||!c.model)continue;
      html+='<div class="setting-row" style="border-bottom:1px solid rgba(255,255,255,0.04);">';
      html+='<span class="setting-label" style="font-size:12px;">'+(roles[role]||role)+'</span>';
      html+='<span class="setting-value" style="font-size:11px;color:var(--gold);">'+c.model.substring(0,30)+'</span>';
      html+='</div>';
    }
    html+='<div style="margin-top:16px;font-weight:600;color:var(--text);margin-bottom:8px;">'+__('model.switch')+'</div>';
    if(_providersData.length>0){
      html+='<div style="margin-bottom:10px;"><select id="model-provider-select" style="width:100%;padding:8px 10px;background:var(--bg);border:1px solid var(--border);border-radius:4px;color:var(--text);font-size:13px;outline:none;cursor:pointer;';
      html+='-webkit-appearance:none;appearance:none;">';
      html+='<option value="" style="color:#222;background:#f0f0f0;">'+__('model.select_provider')+'</option>';
      for(var i=0;i<_providersData.length;i++){
        var p=_providersData[i];
        html+='<option value="'+escHtml(p.id)+'" style="color:#222;background:#f0f0f0;">'+escHtml(p.name)+'</option>';
      }
      html+='</select></div>';
    }
    html+='<div id="model-switch-form" style="display:none;padding:12px;background:var(--card);border:1px solid var(--gold);border-radius:6px;">';
    html+='  <div id="switch-provider-name" style="margin-bottom:8px;font-weight:600;color:var(--gold);font-size:13px;"></div>';
    html+='  <div style="margin-bottom:6px;"><label style="display:block;font-size:11px;color:var(--dim);margin-bottom:2px;">'+__('model.base_url')+'</label>';
    html+='    <input id="switch-base-url" type="text" style="width:100%;padding:7px 10px;background:var(--bg);border:1px solid var(--border);border-radius:4px;color:var(--text);font-size:12px;outline:none;box-sizing:border-box;"></div>';
    html+='  <div style="margin-bottom:6px;"><label style="display:block;font-size:11px;color:var(--dim);margin-bottom:2px;">'+__('model.api_endpoint')+'</label>';
    html+='    <input id="switch-endpoint" type="text" style="width:100%;padding:7px 10px;background:var(--bg);border:1px solid var(--border);border-radius:4px;color:var(--text);font-size:12px;outline:none;box-sizing:border-box;"></div>';
    html+='  <div style="margin-bottom:8px;"><label style="display:block;font-size:11px;color:var(--dim);margin-bottom:2px;">'+__('model.api_key')+'</label>';
    html+='    <input id="switch-api-key" type="text" style="width:100%;padding:7px 10px;background:var(--bg);border:1px solid var(--border);border-radius:4px;color:var(--text);font-size:12px;outline:none;box-sizing:border-box;"></div>';
    html+='  <div style="display:flex;gap:6px;">';
    html+='    <button id="switch-confirm-btn" style="flex:1;padding:6px;background:var(--gold);color:#050816;border:none;border-radius:4px;cursor:pointer;font-weight:600;font-size:12px;">'+__('model.confirm_switch')+'</button>';
    html+='    <button id="switch-cancel-btn" style="flex:1;padding:6px;background:var(--card);border:1px solid var(--border);color:var(--sec);border-radius:4px;cursor:pointer;font-size:12px;">'+__('model.cancel')+'</button>';
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
        document.getElementById('switch-provider-name').textContent=__('model.switch_to')+' '+provider.name;
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
  }).catch(function(){panel.innerHTML='<div style="color:var(--dim);font-style:italic;">模型信息不可用</div>';});
}

function confirmModelSwitch(){
  var sel=document.getElementById('model-provider-select');
  var resultEl=document.getElementById('switch-result');
  if(!sel||!resultEl)return;
  var providerId=sel.value;
  if(!providerId){resultEl.innerHTML='<span style="color:var(--orange);">'+__('model.no_provider')+'</span>';return;}
  var baseUrl=document.getElementById('switch-base-url')?document.getElementById('switch-base-url').value.trim():'';
  var endpoint=document.getElementById('switch-endpoint')?document.getElementById('switch-endpoint').value.trim():'';
  var apiKey=document.getElementById('switch-api-key')?document.getElementById('switch-api-key').value.trim():'';
  resultEl.innerHTML='⏳ '+__('model.switching');
  fetch(API+'/api/models/switch',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({provider_id:providerId,base_url:baseUrl,endpoint:endpoint,api_key:apiKey})}).then(function(r){return r.json();}).then(function(d){
    if(d.ok){resultEl.innerHTML='<span style="color:var(--green);">✔ '+escHtml(d.message)+'</span>';setTimeout(function(){refreshModelPanel();},1500);}
    else{resultEl.innerHTML='<span style="color:var(--orange);">❌ '+escHtml(d.error)+'</span>';}
  }).catch(function(){resultEl.innerHTML='<span style="color:var(--orange);">❌ '+__('model.req_fail')+'</span>';});
}
function isWebGL2Available(){try{const c=document.createElement('canvas');return !!(window.WebGL2RenderingContext&&c.getContext('webgl2'));}catch(e){return false;}}
const CAN_3D = isWebGL2Available();
let USE_3D = false;
let _gfxSettings = {};
let _gfxNodeLimit = 700;
let _gfxRotationSpeed = 1;
let _gfxNodeSizeScale = 1;
let _gfxLayoutMode = 'spiral';

let NODE_COUNT = 700;
let nodeData = [];
let nodeMetaData = {};
let t = 0;

// 2D 视图变换（缩放 + 位移，双击聚焦时使用）
let viewX = 0, viewY = 0, viewScale = 1;

function screenToWorld(sx, sy){
  return {x: (sx - viewX) / viewScale, y: (sy - viewY) / viewScale};
}

function createNodeData(n){
  nodeData=[];nodeMetaData={};
  nodeData.push({index:0,name:'太初',x:0,y:0,galR:0,galAngle:0,baseSize:20,
    gravity:0,hotspot:0,clusterId:0,_3dx:0,_3dy:0,_3dz:0,_3dRadius:0,_3dAngle:0,
    evolution:null,dependencies:[],summary:'太初知识宇宙核心'});
  var isSpiral=_gfxLayoutMode!=='circle';
  // Neural cluster centers
  var numClusters=4,clusterCenters=[];
  if(!isSpiral){
    for(var ci=0;ci<numClusters;ci++){
      var ca=(ci/numClusters)*Math.PI*2+0.3;
      var cr=100+Math.random()*120;
      clusterCenters.push({x:Math.cos(ca)*cr,y:Math.sin(ca)*cr*0.6,spread:50+Math.random()*50});
    }
  }
  for(let i=1;i<n;i++){
    var r,angle,scatter,clusterId;
    if(isSpiral){
      const arms=4;
      r=60+Math.random()*450;
      scatter=r*0.025;
      angle=(i/n)*Math.PI*12+((i%arms)/arms)*Math.PI*2+(Math.random()-0.5)*scatter;
      clusterId=Math.floor(((angle%(Math.PI*2))/(Math.PI*2))*7);
    }else{
      var cc=clusterCenters[i%numClusters];
      var a=Math.random()*Math.PI*2;
      var rd=Math.random()*cc.spread;
      var nx=cc.x+Math.cos(a)*rd,ny=cc.y+Math.sin(a)*rd;
      angle=Math.atan2(ny,nx);
      r=Math.sqrt(nx*nx+ny*ny);
      clusterId=i%numClusters;
    }
    const gravityNorm=isSpiral?1-(r/550):0.5;
    const grav=0.5+gravityNorm*4.5;
    nodeData.push({index:i,name:'Node_'+i,x:0,y:0,galR:r,galAngle:angle,baseSize:1.5+gravityNorm*10,
      gravity:grav,hotspot:Math.random()*0.5,clusterId:clusterId,_3dx:0,_3dy:0,_3dz:0,_3dRadius:r,_3dAngle:angle,
      evolution:{generation:0,fitness_results:[Math.random(),Math.random(),Math.random(),Math.random(),Math.random()]},dependencies:[],summary:''});
  }
  // 边
  for(var j=1;j<nodeData.length;j++){var nd=nodeData[j];
    if(!isSpiral){
      // Neural: connect to same-cluster nodes
      for(var k=0;k<3;k++){var ri=Math.floor(Math.random()*n);if(ri!==nd.index&&ri>0)nd.dependencies.push(ri);}
    }else{
      for(var k=0;k<Math.floor(Math.random()*2);k++){var ri=Math.floor(Math.random()*n);if(ri!==nd.index){
        if(Math.abs(nodeData[ri].galR-nd.galR)<50)nd.dependencies.push(ri);}}
    }
  }
}

async function loadRealGraph(){
  try{const r=await fetch(API+'/api/kb/graph?limit=0');const d=await r.json();
    if(!d.nodes||d.nodes.length===0){createNodeData(NODE_COUNT);resizeCanvas2D();initNodePositions();return;}
    // 前置太初节点
    d.nodes.unshift({id:'太初',label:'太初',summary:'太初知识宇宙核心',gravity:0});
    NODE_COUNT=d.nodes.length;
    // id → index 映射，用于边查找
    var idToIndex={};d.nodes.forEach(function(n,i){idToIndex[n.id]=i;});
    // Neural cluster centers (for circle mode)
    var ncxs=[],ncys=[],nspreads=[];
    if(_gfxLayoutMode==='circle'){
      for(var ci=0;ci<4;ci++){var ca=(ci/4)*Math.PI*2+0.3;var cr=100+Math.random()*120;
        ncxs.push(Math.cos(ca)*cr);ncys.push(Math.sin(ca)*cr*0.6);nspreads.push(50+Math.random()*50);}
    }
    nodeData=d.nodes.map(function(n,i){
      if(i===0)return{index:0,name:'太初',x:0,y:0,galR:0,galAngle:0,baseSize:20,
        gravity:0,hotspot:0,clusterId:0,_3dx:0,_3dy:0,_3dz:0,_3dRadius:0,_3dAngle:0,
        evolution:null,dependencies:[],summary:n.summary||'太初知识宇宙核心'};
      var r,angle;
      if(_gfxLayoutMode==='circle'){
        var ci=(i-1)%4;var a=Math.random()*Math.PI*2;var rd=Math.random()*nspreads[ci];
        var nx=ncxs[ci]+Math.cos(a)*rd,ny=ncys[ci]+Math.sin(a)*rd;
        r=Math.sqrt(nx*nx+ny*ny);angle=Math.atan2(ny,nx);
      }else{
        r=60+Math.random()*450;angle=(i/NODE_COUNT)*Math.PI*12;
      }
      return{index:i,name:n.label||n.id,x:0,y:0,galR:r,galAngle:angle,baseSize:4+Math.random()*8,
        gravity:n.gravity||Math.random()*3,hotspot:0,clusterId:i%7,evolution:null,dependencies:[],summary:n.summary||'',
        _3dx:0,_3dy:0,_3dz:0,_3dRadius:r,_3dAngle:angle};
    });
    // 将 API 边映射到 dependencies（太初索引为0，API原节点索引自动+1，但边用id查找所以正确）
    if(d.edges){d.edges.forEach(function(e){
      var fi=idToIndex[e.from],ti=idToIndex[e.to];
      if(fi!==undefined&&ti!==undefined){nodeData[fi].dependencies.push(ti);nodeData[ti].dependencies.push(fi);}
    });}
    document.getElementById('nodeCountText').innerText=NODE_COUNT;resizeCanvas2D();initNodePositions();
  }catch(e){console.error('[loadRealGraph] fallback to synthetic:',e);createNodeData(NODE_COUNT);resizeCanvas2D();initNodePositions();}
}

function initNodePositions(){
  if(!canvas2d)return;const cx=canvas2d.width/2,cy=canvas2d.height/2;
  nodeData.forEach(function(n){n.x=cx+n.galR*Math.cos(n.galAngle);n.y=cy+n.galR*Math.sin(n.galAngle)*0.6;
    n._3dx=n.x-cx;n._3dy=(Math.random()-0.5)*22;n._3dz=n.y-cy;});
}

const panelContent=document.getElementById('panel-content');
const miniChartCanvas=document.getElementById('miniChart');
const miniCtx=miniChartCanvas?miniChartCanvas.getContext('2d'):null;
function drawMiniChart(f){if(!miniCtx)return;
  miniCtx.fillStyle="#111";miniCtx.fillRect(0,0,miniChartCanvas.width,miniChartCanvas.height);if(!f||f.length<2)return;
  miniCtx.strokeStyle="#0f0";miniCtx.lineWidth=2;miniCtx.beginPath();const step=miniChartCanvas.width/(f.length-1);
  f.forEach(function(v,i){const y=miniChartCanvas.height*(1-Math.max(0,Math.min(1,v)));if(i===0)miniCtx.moveTo(0,y);else miniCtx.lineTo(i*step,y);});
  miniCtx.stroke();miniCtx.lineTo((f.length-1)*step,miniChartCanvas.height);miniCtx.lineTo(0,miniChartCanvas.height);miniCtx.closePath();
  miniCtx.fillStyle='rgba(0,255,0,0.05)';miniCtx.fill();}
function showPanelInfo(idx){const n=nodeData[idx];if(!n)return;const meta=nodeMetaData['N'+idx]||{};
  let html='<div style="font-weight:600;color:#7dd3fc;margin-bottom:4px;">'+(n.name||'Node_'+idx)+'</div>';
  if(n.summary)html+='<div style="font-size:11px;color:#ccc;margin-bottom:6px;">'+n.summary+'</div>';
  // 关联链接（真实图谱 API 数据）
  if(n.dependencies&&n.dependencies.length>0){
    html+='<div style="font-size:11px;color:rgba(255,255,255,0.4);margin-bottom:3px;">'+__('panel.neighbors')+' ('+n.dependencies.length+'):</div>';
    var depNames=n.dependencies.slice(0,10).map(function(di){var dn=nodeData[di];return dn?dn.name:'?'}).filter(function(x){return x!=='?';});
    if(depNames.length>0)html+='<div style="font-size:11px;color:#7dd3fc;line-height:1.6;">'+depNames.join(' · ')+'</div>';
  }
  // 运行时数据（WS 推送）
  var rt=[];
  if(n.clusterId!==undefined)rt.push('🔘 '+__('panel.cluster')+': '+n.clusterId);
  if(n.gravity!==undefined)rt.push('🌌 '+__('panel.gravity')+': '+n.gravity.toFixed(2));
  if(n.hotspot!==undefined)rt.push('🔥 Hotspot: '+n.hotspot.toFixed(2));
  if(meta.archive_id)rt.push('📦 ID: '+meta.archive_id);
  if(meta.file_name)rt.push('📄 '+meta.file_name);
  if(rt.length>0)html+='<div style="font-size:11px;color:#888;line-height:1.6;margin-top:4px;">'+rt.join('<br>')+'</div>';
  panelContent.innerHTML=html;
  // evolution fitness chart（仅合成节点有）
  if(n.evolution&&n.evolution.fitness_results)drawMiniChart(n.evolution.fitness_results);
  else if(miniCtx){miniCtx.fillStyle="#111";miniCtx.fillRect(0,0,miniChartCanvas.width,miniChartCanvas.height);}
}
function clearPanelInfo(){panelContent.innerHTML=__('panel.placeholder');}

function doNebulaSearch(){
  var q=document.getElementById('nebula-search-input');
  if(!q||!q.value.trim())return;
  var query=q.value.trim().toLowerCase();
  var found=-1;
  for(var i=0;i<nodeData.length;i++){
    if(nodeData[i].name.toLowerCase().indexOf(query)!==-1){found=i;break;}
  }
  if(found===-1){
    panelContent.innerHTML='<div style="color:var(--orange);">'+__('panel.not_found')+': '+escHtml(q.value.trim())+'</div>';
    return;
  }
  var n=nodeData[found];
  if(USE_3D){
    // 3D: 先切回2D再定位（简单处理）
    document.getElementById('mode3d').checked=false;
    document.getElementById('mode3d').dispatchEvent(new Event('change'));
  }
  // 2D 定位
  var cvs=canvas2d;
  if(cvs){
    var w=cvs.width/2,h=cvs.height/2;
    viewX=w-n.x*viewScale;
    viewY=h-n.y*viewScale;
    if(viewScale<2)viewScale=2;
  }
  showPanelInfo(found);
  q.value='';
}

let ws=null;
function connectWS(){try{ws=new WebSocket('ws://127.0.0.1:8765/ws');
    ws.onopen=function(){document.getElementById('ws-status').className='online';document.getElementById('ws-status').innerHTML=__('ws.online');document.getElementById('set-ws-status').innerHTML='<span class="ok">'+__('ws.online')+'</span>';};
    ws.onmessage=function(ev){try{const d=JSON.parse(ev.data);
        nodeData.forEach(function(n){const g=d.semantic_gravity?.[n.name];if(g!==undefined)n.gravity=g;const hot=d.attention_map?.[n.name];if(hot!==undefined)n.hotspot=hot;const aff=d.agent_affinity?.[n.name];if(aff!==undefined)n.clusterId=Math.floor(aff);});
        if(d.evolution)nodeData.forEach(function(n){n.evolution=d.evolution;});if(d.archive_hotspots){d.archive_hotspots.forEach(function(h,idx){const nd=nodeData[idx];if(nd&&h.dependencies)nd.dependencies=h.dependencies;});}
        if(d.node_meta){Object.entries(d.node_meta).forEach(function(e){nodeMetaData[e[0]]=Object.assign(nodeMetaData[e[0]]||{},e[1]);});}}catch(e){}};
    ws.onclose=function(){document.getElementById('ws-status').className='offline';document.getElementById('ws-status').innerHTML=__('ws.offline');document.getElementById('set-ws-status').innerHTML='<span class="err">'+__('ws.offline')+'</span>';setTimeout(connectWS,3000);};
  }catch(e){setTimeout(connectWS,3000);}}

	// gfx settings loaded via loadGfxSettings() + renderGfxPanel() from refreshSettings()

// ==================== 2D 银河星云引擎 ====================
const canvas2d=document.getElementById('canvas2d');
const ctx=canvas2d.getContext('2d');
let hoverIndex2D=-1;
let lastFrameTime=performance.now(),frameTimes=[];
let fpsLimit=60;

function resizeCanvas2D(){if(!canvas2d)return;
  var w=canvas2d.clientWidth||window.innerWidth;
  var h=canvas2d.clientHeight||window.innerHeight;
  if(w>0&&h>0&&(canvas2d.width!==w||canvas2d.height!==h)){canvas2d.width=w;canvas2d.height=h;}
}

function adaptiveNodeCount2D(){
  const now=performance.now();const dt=now-lastFrameTime;lastFrameTime=now;
  frameTimes.push(dt);if(frameTimes.length>30)frameTimes.shift();
  const fps=1000/(frameTimes.reduce(function(a,b){return a+b;},0)/frameTimes.length);
  if(fps>fpsLimit)return;
  let target=NODE_COUNT;
  if(fps<25)target=Math.max(500,Math.floor(NODE_COUNT*0.95));
  else if(fps>50)target=Math.min(1000,Math.floor(NODE_COUNT*1.05));
  if(target!==NODE_COUNT){
    if(target>NODE_COUNT){const add=target-NODE_COUNT;for(let i=0;i<add;i++){const idx=NODE_COUNT+i;const r=60+Math.random()*450;const angle=(idx/target)*Math.PI*12;
      nodeData.push({index:idx,name:'Node_'+idx,x:0,y:0,galR:r,galAngle:angle,baseSize:4+Math.random()*8,gravity:Math.random()*5,hotspot:Math.random(),clusterId:Math.floor(Math.random()*7),evolution:{generation:0,fitness_results:[Math.random(),Math.random(),Math.random(),Math.random(),Math.random()]},dependencies:[],summary:'',_3dx:0,_3dy:0,_3dz:0,_3dRadius:r,_3dAngle:angle});}
    }else nodeData.splice(target);
    NODE_COUNT=target;document.getElementById('nodeCountText').innerText=NODE_COUNT;
  }
}

function animate2D(){
  if(USE_3D){requestAnimationFrame(animate2D);return;}t+=0.02;adaptiveNodeCount2D();
  const w=canvas2d.width,h=canvas2d.height;if(w===0||h===0){resizeCanvas2D();return;}
  const cx=w/2,cy=h/2;
  ctx.fillStyle='#000';ctx.fillRect(0,0,w,h);

  // 应用视图变换（缩放 + 位移）
  ctx.save();
  ctx.translate(viewX, viewY);
  ctx.scale(viewScale, viewScale);

  // 中心光晕
  var grd=ctx.createRadialGradient(cx,cy,0,cx,cy,60);
  grd.addColorStop(0,'rgba(255,200,100,0.06)');grd.addColorStop(1,'rgba(255,200,100,0)');
  ctx.fillStyle=grd;ctx.beginPath();ctx.arc(cx,cy,60,0,Math.PI*2);ctx.fill();

  // 重心吸引线
  ctx.strokeStyle='rgba(255,255,255,0.008)';ctx.lineWidth=0.3;
  nodeData.forEach(function(n){ctx.beginPath();ctx.moveTo(cx,cy);ctx.lineTo(n.x,n.y);ctx.stroke();});

  // 神经网络模式：绘制全部连线
  if(_gfxLayoutMode==='circle'){
    ctx.strokeStyle='rgba(100,200,255,0.35)';ctx.lineWidth=0.8;
    for(var _ni=1;_ni<nodeData.length;_ni++){var _nn=nodeData[_ni];
      if(!_nn.dependencies)continue;
      for(var _di=0;_di<_nn.dependencies.length;_di++){var _dn=nodeData[_nn.dependencies[_di]];
        if(_dn&&_dn.index>_ni){ctx.beginPath();ctx.moveTo(_nn.x,_nn.y);ctx.lineTo(_dn.x,_dn.y);ctx.stroke();}
      }
    }
  }

  // 差速旋转 + 绘制（从 i=1 跳过中心太初节点）
  for(var i=1;i<nodeData.length;i++){var n=nodeData[i];
    if(_gfxLayoutMode!=='circle'){
      const speed=0.008/(n.galR*0.02+0.3)*_gfxRotationSpeed;
      n.galAngle+=speed;
    }
    n.x=cx+n.galR*Math.cos(n.galAngle);
    n.y=cy+n.galR*Math.sin(n.galAngle)*0.6;

    const size=n.baseSize+n.gravity*0.5;
    const isHover=(i===hoverIndex2D);
    // 无闪烁，亮度由 hotspot 数据驱动
    const alpha=Math.max(0.3,0.45+n.hotspot*0.4);

    ctx.beginPath();ctx.arc(n.x,n.y,isHover?size*1.5:size,0,Math.PI*2);
    // 2D 单一蓝色
    ctx.fillStyle='hsla(210,100%,'+(isHover?70:50)+'%,'+alpha+')';
    ctx.fill();

    if(isHover){ctx.strokeStyle='#fff';ctx.lineWidth=1;ctx.stroke();}

    // DAG 依赖线
    if(isHover&&n.dependencies){
      ctx.strokeStyle='rgba(255,100,100,0.3)';ctx.lineWidth=1;
      n.dependencies.forEach(function(dep){const d=nodeData[dep];if(d){ctx.beginPath();ctx.moveTo(n.x,n.y);ctx.lineTo(d.x,d.y);ctx.stroke();}});
    }
  }

  // 中心「太初」节点（覆盖在最上层）
  {
    var g=ctx.createRadialGradient(cx,cy,0,cx,cy,60);
    g.addColorStop(0,'rgba(255,210,90,0.15)');g.addColorStop(1,'rgba(255,210,90,0)');
    ctx.fillStyle=g;ctx.beginPath();ctx.arc(cx,cy,60,0,Math.PI*2);ctx.fill();
    ctx.beginPath();ctx.arc(cx,cy,20,0,Math.PI*2);
    ctx.fillStyle='rgba(255,220,100,0.95)';ctx.fill();
    ctx.strokeStyle='rgba(255,240,180,0.5)';ctx.lineWidth=2;ctx.stroke();
    // 标签
    ctx.fillStyle='rgba(255,255,255,0.8)';ctx.font='bold 12px sans-serif';ctx.textAlign='center';
    ctx.fillText('太初',cx,cy+36);
  }
  ctx.restore();
  requestAnimationFrame(animate2D);
}

function startAnimation(){resizeCanvas2D();
  // 强制启动动画，不管 canvas 尺寸
  if(canvas2d.width===0||canvas2d.height===0){resizeCanvas2D();}
  initNodePositions();animate2D();}

canvas2d.addEventListener('mousemove',function(e){if(USE_3D)return;const p=screenToWorld(e.offsetX,e.offsetY);hoverIndex2D=-1;
  for(var i=0;i<nodeData.length;i++){var n=nodeData[i];if(Math.hypot(p.x-n.x,p.y-n.y)<Math.max(5,n.baseSize)){hoverIndex2D=i;showPanelInfo(i);drawMiniChart(n.evolution?n.evolution.fitness_results:null);return;}}clearPanelInfo();});

// 滚轮缩放
canvas2d.addEventListener('wheel',function(e){e.preventDefault();
  var f=e.deltaY>0?0.9:1.1;var ns=Math.max(0.1,Math.min(20,viewScale*f));
  viewX=e.offsetX-(e.offsetX-viewX)*(ns/viewScale);viewY=e.offsetY-(e.offsetY-viewY)*(ns/viewScale);viewScale=ns;},{passive:false});

// 双击聚焦
canvas2d.addEventListener('dblclick',function(e){var p=screenToWorld(e.offsetX,e.offsetY);var ci=-1,md=Infinity;
  for(var i=0;i<nodeData.length;i++){var d=Math.hypot(p.x-nodeData[i].x,p.y-nodeData[i].y);if(d<md){md=d;ci=i;}}
  if(ci>=0&&md<150){var w=canvas2d.width,h=canvas2d.height;
    viewX=w/2-nodeData[ci].x*viewScale;viewY=h/2-nodeData[ci].y*viewScale;
    if(viewScale<2)viewScale=2;showPanelInfo(ci);}});
window.addEventListener('resize',function(){resizeCanvas2D();resizeThree();});

// ==================== 3D 神经突触星云 (Mesh星球 + 圆柱体航道) ====================
let threeScene=null,threeCamera=null,threeRenderer=null;
let planetMeshes=[],synapseMeshes=[],starfield=null,coreRing=null,coreGlow=null;
let raycaster=null,mouse=null,hovered3D=null,clickTarget3D=null;
let camTheta=0,camPhi=1.2,camDist=120;
let isDragging=false,prevMouse={x:0,y:0};
let threeTime=0;

function initScene3D(){
  if(threeScene)return;
  const canvas=document.getElementById('canvas3d');
  threeScene=new THREE.Scene();
  threeCamera=new THREE.PerspectiveCamera(45,window.innerWidth/window.innerHeight,0.1,500);
  threeCamera.position.set(0,60,100);
  threeRenderer=new THREE.WebGLRenderer({canvas:canvas,antialias:true,alpha:true});
  threeRenderer.setSize(window.innerWidth,window.innerHeight);
  threeRenderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
  threeRenderer.setClearColor(0x050816,1);
  raycaster=new THREE.Raycaster();mouse=new THREE.Vector2();
  const ambient=new THREE.AmbientLight(0x303050);ambient.intensity=0.6;threeScene.add(ambient);
  const pl=new THREE.PointLight(0xffaa44,1.5,0);pl.position.set(0,0,0);threeScene.add(pl);
  const pl2=new THREE.PointLight(0x4488ff,0.5,0);pl2.position.set(-60,20,60);threeScene.add(pl2);

  // 星空背景
  const sg=new THREE.BufferGeometry();const sp=new Float32Array(4000*3);
  for(let i=0;i<4000*3;i+=3){sp[i]=(Math.random()-0.5)*500;sp[i+1]=(Math.random()-0.5)*250;sp[i+2]=(Math.random()-0.5)*500;}
  sg.setAttribute('position',new THREE.BufferAttribute(sp,3));
  starfield=new THREE.Points(sg,new THREE.PointsMaterial({color:0xffffff,size:0.2,transparent:true,opacity:0.8}));threeScene.add(starfield);

  // 中心奇点 — 多层发光球
  const coreMat1=new THREE.MeshBasicMaterial({color:0xffaa44,transparent:true,opacity:0.5});
  const core1=new THREE.Mesh(new THREE.SphereGeometry(2.2,48,48),coreMat1);threeScene.add(core1);
  const coreMat2=new THREE.MeshBasicMaterial({color:0xff6600,transparent:true,opacity:0.8});
  const core2=new THREE.Mesh(new THREE.SphereGeometry(1.2,32,32),coreMat2);threeScene.add(core2);
  // 核心光晕 — 使用圆环
  const rg=new THREE.RingGeometry(2.5,4.5,80);coreGlow=new THREE.Mesh(rg,new THREE.MeshBasicMaterial({
    color:0xff8844,side:THREE.DoubleSide,transparent:true,opacity:0.15}));
  coreGlow.rotation.x=Math.PI/2;threeScene.add(coreGlow);
  coreRing=new THREE.Mesh(new THREE.RingGeometry(3.5,4.0,64),
    new THREE.MeshBasicMaterial({color:0xffaa66,side:THREE.DoubleSide,transparent:true,opacity:0.3}));
  coreRing.rotation.x=Math.PI/3;threeScene.add(coreRing);

  buildNebula3D();

  canvas.addEventListener('mousedown',function(e){isDragging=true;prevMouse.x=e.clientX;prevMouse.y=e.clientY;});
  window.addEventListener('mouseup',function(){isDragging=false;});
  canvas.addEventListener('mousemove',function(e){
    if(isDragging){const dx=e.clientX-prevMouse.x,dy=e.clientY-prevMouse.y;camTheta-=dx*0.005;camPhi=Math.max(0.1,Math.min(Math.PI-0.1,camPhi+dy*0.005));prevMouse.x=e.clientX;prevMouse.y=e.clientY;return;}
    const rect=canvas.getBoundingClientRect();mouse.x=((e.clientX-rect.left)/rect.width)*2-1;mouse.y=-((e.clientY-rect.top)/rect.height)*2+1;
    raycaster.setFromCamera(mouse,threeCamera);const intersects=raycaster.intersectObjects(planetMeshes);
    if(intersects.length>0){const obj=intersects[0].object;const data=obj.userData;hovered3D=data.idx;showPanelInfo(data.idx);
      obj.material.emissiveIntensity=Math.min(0.8,obj.material.emissiveIntensity+0.05);
    }else{if(hovered3D!==null){const prev=planetMeshes.find(p=>p.userData.idx===hovered3D);if(prev)prev.material.emissiveIntensity=0.25;}hovered3D=null;if(!clickTarget3D)clearPanelInfo();}});
  canvas.addEventListener('click',function(){if(hovered3D!==null){clickTarget3D=(clickTarget3D===hovered3D)?null:hovered3D;if(clickTarget3D!==null)showPanelInfo(clickTarget3D);else clearPanelInfo();}else{clickTarget3D=null;clearPanelInfo();}});
  canvas.addEventListener('wheel',function(e){camDist=Math.max(20,Math.min(300,camDist+e.deltaY*0.1));e.preventDefault();},{passive:false});
  animate3D();
}

function buildNebula3D(){
  // 清理旧的 if any
  planetMeshes.forEach(function(m){threeScene.remove(m);});planetMeshes=[];
  synapseMeshes.forEach(function(s){threeScene.remove(s.mesh);});synapseMeshes=[];

  // 计算节点度和边权重
  const degree={};nodeData.forEach(function(n){degree[n.index]=0;});
  nodeData.forEach(function(n){(n.dependencies||[]).forEach(function(dep){
    if(degree[dep]!==undefined)degree[dep]=(degree[dep]||0)+1;degree[n.index]=(degree[n.index]||0)+1;});});
  const maxDegree=Math.max(...Object.values(degree),1);
  const edgeWeight={};nodeData.forEach(function(n){(n.dependencies||[]).forEach(function(dep){
    const key=n.index<dep?n.index+'|'+dep:dep+'|'+n.index;edgeWeight[key]=(edgeWeight[key]||0)+1;});});
  const maxWeight=Math.max(...Object.values(edgeWeight),1);

  // --- 构建 Mesh 星球 ---
  nodeData.forEach(function(n,i){
    if(n._3dRadius===undefined){n._3dRadius=n.galR;n._3dAngle=n.galAngle;n._3dy=(Math.random()-0.5)*22;}
    n._3dx=Math.cos(n._3dAngle)*n._3dRadius;n._3dz=Math.sin(n._3dAngle)*n._3dRadius;
    const d=degree[n.index]||0;
    // 色相映射到 clusterId (0-6 -> 0-360度), 饱和度固定 0.8, 亮度关联 degree
    const hue=(n.clusterId/7)*360;
    const normalizedDegree=d/maxDegree;
    const size=0.4+normalizedDegree*2.0;
    const brightness=0.4+normalizedDegree*0.4;
    const color=new THREE.Color('hsl('+hue+',80%,'+(brightness*60+20)+'%)');
    const geo=new THREE.SphereGeometry(size,16,16);
    const mat=new THREE.MeshStandardMaterial({
      color:color,
      emissive:color,
      emissiveIntensity:0.25,
      roughness:0.3,
      metalness:0.1
    });
    const mesh=new THREE.Mesh(geo,mat);
    mesh.position.set(n._3dx,n._3dy,n._3dz);
    mesh.userData={idx:n.index,id:n.name,label:n.name,summary:n.summary||'',degree:d,clusterId:n.clusterId,baseSize:size};
    threeScene.add(mesh);
    planetMeshes.push(mesh);
  });

  // --- 构建圆柱体突触航道 ---
  Object.entries(edgeWeight).forEach(function([key,weight]){
    const parts=key.split('|');const fromIdx=parseInt(parts[0]),toIdx=parseInt(parts[1]);
    const fromN=nodeData[fromIdx],toN=nodeData[toIdx];if(!fromN||!toN)return;
    const start=new THREE.Vector3(fromN._3dx,fromN._3dy,fromN._3dz);
    const end=new THREE.Vector3(toN._3dx,toN._3dy,toN._3dz);
    const dir=new THREE.Vector3().subVectors(end,start);
    const len=dir.length();if(len<0.1)return;
    const nw=weight/maxWeight;
    const radius=0.05+nw*0.3;
    const segments=Math.max(4,Math.floor(3+nw*5));
    // 根据两端节点 clusterId 的平均值计算色相
    const fromClr=nodeData[fromIdx].clusterId||0;
    const toClr=nodeData[toIdx].clusterId||0;
    const avgHue=((fromClr+toClr)/2/7)*360;
    const opacity=0.15+nw*0.4;
    const geo=new THREE.CylinderGeometry(radius,radius,len,segments);
    const mat=new THREE.MeshStandardMaterial({
      color:new THREE.Color('hsl('+avgHue+',60%,50%)'),
      emissive:new THREE.Color('hsl('+avgHue+',40%,20%)'),
      emissiveIntensity:0.3+nw*0.4,
      transparent:true,
      opacity:opacity,
      roughness:0.3,
      metalness:0.05
    });
    const mesh=new THREE.Mesh(geo,mat);
    const mid=new THREE.Vector3().addVectors(start,end).multiplyScalar(0.5);
    mesh.position.copy(mid);
    mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),dir.clone().normalize());
    threeScene.add(mesh);
    synapseMeshes.push({mesh:mesh,fromIdx:fromIdx,toIdx:toIdx,origLen:len,weight:nw});
  });
}

function animate3D(){
  if(!USE_3D)return;requestAnimationFrame(animate3D);threeTime+=0.008;

  // --- Mesh 星球差速旋转 ---
  planetMeshes.forEach(function(mesh){
    const n=nodeData[mesh.userData.idx];
    if(!n||!n._3dRadius||n._3dRadius<0.5)return;
    // 内圈快外圈慢 — 差速旋转
    const speed=0.015/(n._3dRadius*0.2+0.3)*_gfxRotationSpeed;
    n._3dAngle+=speed;
    n._3dx=Math.cos(n._3dAngle)*n._3dRadius;
    n._3dz=Math.sin(n._3dAngle)*n._3dRadius;
    mesh.position.x=n._3dx;
    mesh.position.z=n._3dz;
    // 脉动发光
    const pulsate=0.8+0.3*Math.sin(threeTime*3+mesh.userData.idx*0.3)*0.5+0.5;
    mesh.material.emissiveIntensity=0.15+pulsate*0.15;
    // 微缩放脉动
    const scalePulse=1+0.03*Math.sin(threeTime*2+mesh.userData.idx*0.5);
    mesh.scale.setScalar(scalePulse);
  });

  // --- 圆柱体突触跟随节点 + 流动发光 ---
  synapseMeshes.forEach(function(item){
    const fromN=nodeData[item.fromIdx],toN=nodeData[item.toIdx];
    if(!fromN||!toN)return;
    const start=new THREE.Vector3(fromN._3dx,fromN._3dy,fromN._3dz);
    const end=new THREE.Vector3(toN._3dx,toN._3dy,toN._3dz);
    const dir=new THREE.Vector3().subVectors(end,start);
    const len=dir.length();if(len<0.1)return;
    const mid=new THREE.Vector3().addVectors(start,end).multiplyScalar(0.5);
    item.mesh.position.copy(mid);
    const scaleY=len/(item.origLen||1);
    item.mesh.scale.set(1,scaleY,1);
    item.mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),dir.clone().normalize());
    // 流动发光动画
    const flow=0.5+0.5*Math.sin(threeTime*2+item.fromIdx*0.1);
    item.mesh.material.emissiveIntensity=0.2+flow*0.5;
    item.mesh.material.opacity=0.1+item.weight*0.3+flow*0.1;
  });

  // 中心奇点脉动
  if(coreGlow){const s=1+Math.sin(threeTime*15)*0.15;coreGlow.scale.set(s,s,s);coreGlow.material.opacity=0.1+0.08*Math.sin(threeTime*20);}
  if(coreRing){const s=1+Math.sin(threeTime*12)*0.1;coreRing.scale.set(s,s,s);coreRing.rotation.z+=0.005;}

  // 星空微旋
  if(starfield)starfield.rotation.y+=0.0003;

  // 摄像头位置
  threeCamera.position.x=camDist*Math.sin(camPhi)*Math.cos(camTheta);
  threeCamera.position.y=camDist*Math.cos(camPhi);
  threeCamera.position.z=camDist*Math.sin(camPhi)*Math.sin(camTheta);
  threeCamera.lookAt(0,0,0);
  threeRenderer.render(threeScene,threeCamera);
}

function resizeThree(){if(threeCamera&&threeRenderer){threeCamera.aspect=window.innerWidth/window.innerHeight;threeCamera.updateProjectionMatrix();threeRenderer.setSize(window.innerWidth,window.innerHeight);}}

function escHtml(s){if(!s)return '';return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/'/g,'&#39;').replace(/"/g,'&quot;');}
function esc(s){return escHtml(s);}

// ==================== Loading 遮罩层 ====================
function showLoading(msg){
  let overlay=document.getElementById('loading-overlay');
  if(!overlay){overlay=document.createElement('div');overlay.id='loading-overlay';document.body.appendChild(overlay);}
  overlay.innerHTML='<div style="text-align:center;"><div class="spinner"></div><div style="margin-top:16px;color:#fff;font-size:14px;">'+escHtml(msg)+'</div></div>';
  overlay.style.display='flex';}
function hideLoading(){const el=document.getElementById('loading-overlay');if(el)el.style.display='none';}
function showResult(msg,type){
  let el=document.getElementById('result-toast');
  if(!el){el=document.createElement('div');el.id='result-toast';document.body.appendChild(el);}
  el.textContent=msg;
  el.style.cssText='position:fixed;bottom:30px;left:50%;transform:translateX(-50%);z-index:10000;padding:10px 20px;border-radius:8px;font-size:13px;color:#fff;'+
    (type==='ok'?'background:rgba(74,222,128,0.9);':'background:rgba(248,113,113,0.9);')+'transition:opacity 0.3s;';
  el.style.display='block';
  setTimeout(function(){el.style.opacity='0';setTimeout(function(){el.style.display='none';el.style.opacity='1';},300);},3000);}

checkAPIBadge();setTimeout(connectWS,1000);setInterval(checkAPIBadge,15000);

// ── Agent 记忆仪表盘 ──

var _memoryPieChart = null;
var _memoryTypeChart = null;

async function refreshMemoryDashboard() {
  try {
    // Fetch agent registry + memory sessions in parallel
    var [agentResp, memResp] = await Promise.all([
      fetch(API+'/api/agents'),
      fetch(API+'/api/kb/memory/sessions?limit=100')
    ]);
    var agentData = await agentResp.json();
    var memData = await memResp.json();
    var sessions = memData.sessions || [];
    var agents = agentData.agents || [];

    var onlineCount = agents.filter(function(a) { return a.online; }).length;
    var m1 = document.getElementById('mem-agent-count');
    if (m1) {
      m1.querySelector('div:first-child').textContent = agents.length;
      m1.querySelector('div:first-child').nextElementSibling.textContent = '接入 Agent (' + onlineCount + ' 在线)';
    }

    var totalMemories = 0;
    var agentMap = {};
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

    var m2 = document.getElementById('mem-total-count');
    var m3 = document.getElementById('mem-session-count');
    if (m2) m2.querySelector('div:first-child').textContent = totalMemories;
    if (m3) m3.querySelector('div:first-child').textContent = sessions.length;

    // Agent pie chart
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
        options: { responsive: false, plugins: { legend: { display: false } } }
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
        options: { responsive: false, plugins: { legend: { display: false } } }
      });
    }

    // Recent sessions
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
    var resp = await fetch(API+'/api/kb/aging/report');
    var report = await resp.json();

    var e1 = document.getElementById('aging-total');
    var e2 = document.getElementById('aging-notice');
    var e3 = document.getElementById('aging-aging');
    var e4 = document.getElementById('aging-stale');
    if (e1) e1.querySelector('div:first-child').textContent = report.total_articles || 0;
    if (e2) e2.querySelector('div:first-child').textContent = (report.tier_distribution && report.tier_distribution.notice) || 0;
    if (e3) e3.querySelector('div:first-child').textContent = (report.tier_distribution && report.tier_distribution.aging) || 0;
    if (e4) e4.querySelector('div:first-child').textContent = (report.tier_distribution && report.tier_distribution.stale) || 0;

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
        options: { responsive: false, plugins: { legend: { display: false } } }
      });
    }

    // Top aged list
    var topResp = await fetch(API+'/api/kb/aging?limit=20');
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
  var resultEl = document.getElementById('aging-action-result');
  if (resultEl) resultEl.textContent = '标记中...';
  try {
    var resp = await fetch(API+'/api/kb/aging/apply', { method: 'POST' });
    var data = await resp.json();
    if (resultEl) resultEl.textContent = __('aging.batch_mark') + ': ' + (data.total || 0) + ' files, ' + (data.flagged || 0) + ' flagged';
    refreshAgingDashboard();
  } catch(e) {
    if (resultEl) resultEl.textContent = __('aging.load_fail') + e.message;
  }
}

// 激活首页 tab，确保画布初始化时父容器可见
document.querySelectorAll('#content-area > div').forEach(function(d){d.style.display='none';});
document.getElementById('tab-home').style.display='block';
// 先加载真实图谱数据，成功后启动动画；失败时 loadRealGraph 内部 fallback 到合成数据
(async function(){
  showLoading('加载星云数据...');
  await loadRealGraph();
  hideLoading();
  startAnimation();
})();
updateLangUI();
