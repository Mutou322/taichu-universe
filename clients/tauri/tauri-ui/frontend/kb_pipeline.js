// ── Pipeline 仪表盘 ──
var _pipelineWS = null;
var _pipelineNetwork = null;
var _pipelineNodes = null;
var _pipelineEdges = null;
var _pipelineAgentColors = ["#FF6F61","#6B5B95","#88B04B","#FFA500","#008080","#FF1493"];
var _pipelineColorMap = {};
var _pipelinePanels = {};

function _agentColor(agentId) {
  if (!_pipelineColorMap[agentId]) {
    var idx = Object.keys(_pipelineColorMap).length % _pipelineAgentColors.length;
    _pipelineColorMap[agentId] = _pipelineAgentColors[idx];
  }
  return _pipelineColorMap[agentId];
}

function _getAgentPanel(agentId) {
  if (!_pipelinePanels[agentId]) {
    var container = document.getElementById('pipeline-timer-list');
    if (!container) return null;
    var panel = document.createElement('div');
    panel.style.cssText = 'margin-bottom:6px;padding:4px;border:1px solid var(--border);border-radius:4px;border-left:3px solid ' + _agentColor(agentId) + ';';
    panel.innerHTML = '<div style="font-size:11px;font-weight:600;margin-bottom:2px;color:' + _agentColor(agentId) + ';">' + agentId + '</div><div id="timers-' + agentId + '"></div>';
    container.appendChild(panel);
    _pipelinePanels[agentId] = panel.querySelector('#timers-' + agentId);
  }
  return _pipelinePanels[agentId];
}

function _logTrace(stage, content) {
  var log = document.getElementById('trace-log');
  if (!log) return;
  var entry = document.createElement('div');
  entry.style.cssText = 'font-size:11px;color:var(--sec);margin-bottom:1px;';
  entry.textContent = '[' + new Date().toLocaleTimeString() + '] ' + stage + ': ' + content;
  log.appendChild(entry);
  log.scrollTop = log.scrollHeight;
}

function initPipelineWS() {
  if (_pipelineWS && _pipelineWS.readyState === WebSocket.OPEN) return;
  try {
    _pipelineWS = new WebSocket('ws://127.0.0.1:8767');
    _pipelineWS.onmessage = function(event) {
      try {
        var msg = JSON.parse(event.data);
        var agentId = (msg.tags && msg.tags.agent_id) || 'agent1';
        // Timer
        if (msg.name && msg.name.indexOf('timer') !== -1) {
          var timersEl = _getAgentPanel(agentId);
          if (timersEl) {
            var el = timersEl.querySelector('#' + msg.name.replace(/\./g, '-'));
            if (!el) {
              el = document.createElement('div');
              el.id = msg.name.replace(/\./g, '-');
              el.style.cssText = 'font-size:11px;margin-bottom:1px;';
              timersEl.appendChild(el);
            }
            el.textContent = msg.name.split('.').pop() + ': ' + Math.round(msg.value || 0) + 'ms';
          }
        }
        // Graph expand
        if (msg.name === 'graph_expand' && msg.tags) {
          initPipelineGraph();
          if (!_pipelineNetwork) return;
          var nodes = msg.tags.nodes || [];
          var edges = msg.tags.edges || [];
          var gravity = msg.tags.semantic_gravity || {};
          for (var n of nodes) {
            var g = gravity[n] || 1;
            if (!_pipelineNodes.get(n)) {
              _pipelineNodes.add({ id: n, label: n.length > 18 ? n.substring(0,16)+'..' : n, value: g, color: _agentColor(agentId), title: 'gravity: ' + g.toFixed(2) });
            } else {
              _pipelineNodes.update({ id: n, value: g, title: 'gravity: ' + g.toFixed(2) });
            }
          }
          for (var e of edges) {
            var key = e[0] + '-' + e[1];
            if (!_pipelineEdges.get(key)) {
              _pipelineEdges.add({ id: key, from: e[0], to: e[1], color: _agentColor(agentId) });
            }
          }
          _pipelineNetwork.stabilize();
        }
        // Context/Trace
        if (msg.name === 'context_builder' && msg.tags) {
          _logTrace(agentId + ' context', 'length=' + (msg.tags.context ? msg.tags.context.length : 0));
        }
        if (msg.tags && msg.tags.trace) {
          _logTrace(agentId + ' ' + msg.name, msg.tags.trace);
        }
      } catch(e) {}
    };
    _pipelineWS.onclose = function() { _pipelineWS = null; };
  } catch(e) {}
}

function initPipelineGraph() {
  var container = document.getElementById('pipeline-graph-container');
  if (!container || _pipelineNetwork) return;
  _pipelineNodes = new vis.DataSet([]);
  _pipelineEdges = new vis.DataSet([]);
  _pipelineNetwork = new vis.Network(container, { nodes: _pipelineNodes, edges: _pipelineEdges }, {
    physics: { enabled: true, solver: 'barnesHut', stabilization: { enabled: true, iterations: 50 } },
    interaction: { dragNodes: true, zoomView: true, tooltipDelay: 100 },
    nodes: { shape: 'dot', font: { color: '#ccc', size: 10 }, borderWidth: 1, scaling: { min: 8, max: 30 } },
    edges: { width: 1, color: { color: '#5a5a8a', hover: '#d4af37' } },
  });
  // 稳定后冻结物理引擎，防止鼠标移动触发抽搐
  _pipelineNetwork.once('stabilizationIterationsDone', function() { _pipelineNetwork.setOptions({ physics: false }); });
}

async function runPipelineFromUI() {
  var box = document.getElementById('pipeline-query-box');
  var q = box ? box.value.trim() : 'transformer attention';
  if (!q) q = 'transformer attention';

  // 清空并重置
  var timerContainer = document.getElementById('pipeline-timer-list');
  if (timerContainer) timerContainer.innerHTML = '<div style="color:var(--dim);font-size:11px;">⏳ 运行中...</div>';
  var traceLog = document.getElementById('trace-log');
  if (traceLog) traceLog.innerHTML = '';
  _pipelinePanels = {};

  try {
    var resp = await fetch(API + '/api/pipeline/trace?q=' + encodeURIComponent(q));
    var d = await resp.json();
    if (d.error) { if (timerContainer) timerContainer.innerHTML = '<span style="color:var(--orange);font-size:11px;">' + d.error + '</span>'; return; }

    // 清空并重建 agent panel
    if (timerContainer) timerContainer.innerHTML = '';
    var agentTimersEl = _getAgentPanel('agent1');
    if (agentTimersEl) {
      var stages = [['query_parser','查询解析'],['vector_search','向量检索'],['graph_expand','图谱扩展'],['ontology_filter','本体过滤'],['rerank','重排序'],['context_builder','上下文组装']];
      for (var s of stages) {
        var ms = d.timers[s[0]] || 0;
        var el = document.createElement('div');
        el.style.cssText = 'font-size:11px;margin-bottom:1px;';
        var barW = Math.min(100, Math.round(ms / (d.total_ms || 1) * 100));
        var color = ms > 1000 ? '\\#e8963e' : ms > 200 ? '\\#d4af37' : '\\#3dd68c';
        el.innerHTML = s[1] + ' <span style="color:' + color + ';">' + ms + 'ms</span><div style="background:var(--surface);border-radius:2px;height:8px;margin-top:1px;"><div style="background:' + color + ';width:' + barW + '%;height:100%;border-radius:2px;"></div></div>';
        agentTimersEl.appendChild(el);
      }
      // 总计
      var totalEl = document.createElement('div');
      totalEl.style.cssText = 'font-size:11px;font-weight:600;margin-top:4px;padding-top:4px;border-top:1px solid var(--border);';
      totalEl.textContent = '总计: ' + d.total_ms + 'ms';
      agentTimersEl.appendChild(totalEl);
    }

    // Metrics
    var metricsEl = document.getElementById('pipeline-metrics-list');
    if (metricsEl) {
      metricsEl.innerHTML =
        '<div style="margin-bottom:3px;">结果: <span style="color:var(--gold);">' + d.result_count + '</span> 条</div>' +
        '<div style="margin-bottom:3px;">图谱扩展: <span style="color:var(--green);">' + d.graph_nodes_expanded + '</span> 节点</div>' +
        '<div style="font-size:10px;color:var(--dim);">查询: ' + d.query.substring(0, 30) + '</div>';
    }

    // Trace
    _logTrace('pipeline', d.result_count + ' results, ' + d.total_ms + 'ms');
    try {
      var resp2 = await fetch(API + '/api/pipeline/trace?q=' + encodeURIComponent(q) + '&context=1');
      var d2 = await resp2.json();
      if (d2.context) {
        _logTrace('context', d2.context.substring(0, 200) + '...');
      }
    } catch(e) {}

  } catch(e) {
    if (timerContainer) timerContainer.innerHTML = '<span style="color:var(--orange);font-size:11px;">API 不可用</span>';
  }
}
