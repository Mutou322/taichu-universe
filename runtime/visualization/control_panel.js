// runtime/visualization/control_panel.js
// Phase 9 — 可交互控制面板

// 创建控制面板
const controlPanel = document.createElement('div');
controlPanel.style.position = 'fixed';
controlPanel.style.top = '10px';
controlPanel.style.left = '10px';
controlPanel.style.padding = '10px';
controlPanel.style.background = '#2b2b2b';
controlPanel.style.border = '1px solid #555';
controlPanel.style.color = '#f0f0f0';
controlPanel.style.zIndex = 1000;
controlPanel.innerHTML = `
  <b>Phase 9 Control Panel</b><br/>
  Shards: <input type="number" id="shardCount" min="1" max="10" value="4"><br/>
  Agents: <input type="number" id="agentCount" min="1" max="10" value="4"><br/>
  Nodes: <input type="number" id="nodeCount" min="1" max="50" value="20"><br/>
  Evolution Speed (ticks/sec): <input type="number" id="evolutionSpeed" min="0.1" max="5" step="0.1" value="1"><br/>
  <button id="applyBtn">Apply</button>
`;
document.body.appendChild(controlPanel);

// WebSocket
const wsControl = new WebSocket("ws://localhost:8767");

wsControl.onopen = function(){
    console.log("Control WS connected");
};

// 初始参数
var controlParams = {
    shardCount: 4,
    agentCount: 4,
    nodeCount: 20,
    evolutionSpeed: 1
};

// Apply 按钮
document.getElementById("applyBtn").onclick = function(){
    controlParams.shardCount = parseInt(document.getElementById("shardCount").value);
    controlParams.agentCount = parseInt(document.getElementById("agentCount").value);
    controlParams.nodeCount = parseInt(document.getElementById("nodeCount").value);
    controlParams.evolutionSpeed = parseFloat(document.getElementById("evolutionSpeed").value);

    wsControl.send(JSON.stringify({
        type: "control_update",
        params: controlParams
    }));
    console.log("Control params sent:", controlParams);
};

// 实时显示当前参数
var paramDisplay = document.createElement('div');
paramDisplay.style.marginTop = '5px';
paramDisplay.style.color = '#ffcc00';
controlPanel.appendChild(paramDisplay);

function updateParamDisplay(){
    paramDisplay.innerHTML = "Shards=" + controlParams.shardCount +
        ", Agents=" + controlParams.agentCount +
        ", Nodes=" + controlParams.nodeCount +
        ", Speed=" + controlParams.evolutionSpeed;
}
setInterval(updateParamDisplay, 500);
