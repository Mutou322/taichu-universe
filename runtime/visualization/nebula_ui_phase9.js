// runtime/visualization/nebula_ui_phase9.js
// Phase 9 — Nebula UI 全景面板
// 需要 vis-network 已初始化，network: vis.Network 实例
// panel IDs: #evolutionPanel, #attentionPanel, #gbrainPanel, #hotspotPanel, #shardPanel

const shardColors = ["#ff6666", "#66ff66", "#6666ff", "#ffcc66"];
const agentColors = ["#cc33ff", "#33ccff", "#ff9933", "#33ffcc"];

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);

    // 1. Evolution metrics
    if(data.type === "evolution"){
        updateEvolutionPanel(data);
    }

    // 2. Node attention / semantic gravity
    if(data.type === "attention_map"){
        updateAttentionMap(data, data.semantic_gravity);
    }

    // 3. GBrain clusters
    if(data.type === "gbrain"){
        updateGBrainPanel(data.clusters, data.gravity);
    }

    // 4. Hotspot clusters
    if(data.type === "hotspot_clusters"){
        updateHotspotPanel(data);
    }

    // 5. Shard & Agent Cluster
    if(data.type === "ecosystem"){
        updateShardPanel(
            data.node_clusters,
            data.agent_clusters
        );
    }
};

// ------------------- Panel update functions -------------------

function updateEvolutionPanel(evolution){
    const panel = document.getElementById("evolutionPanel");
    if(!panel) return;
    const div = document.createElement("div");
    const bestFitness = Math.max.apply(null, evolution.fitness_results);
    div.innerHTML = "<b>Gen " + evolution.generation + "</b>: " +
        "Best Fitness=" + bestFitness.toFixed(4) + ", " +
        "Genome=" + JSON.stringify(evolution.best_genome);
    panel.appendChild(div);
    panel.scrollTop = panel.scrollHeight;
}

function updateAttentionMap(attention, semanticGravity){
    if(!window.network) return;
    Object.entries(attention).forEach(function(entry){
        const node = entry[0];
        const weight = entry[1];
        const n = network.body.nodes[node];
        if(n){
            const gravity = (semanticGravity && semanticGravity[node]) || 0;
            const r = Math.min(255, Math.floor(weight * 50 + gravity * 10));
            const g = 255 - Math.floor(weight * 50);
            n.color = "rgb(" + r + "," + g + ",100)";
            n.size = 20 + gravity * 2;
        }
    });
    network.redraw();
}

function updateGBrainPanel(clusters, gravity){
    const panel = document.getElementById("gbrainPanel");
    if(!panel) return;
    panel.innerHTML = "<pre>Clusters: " + JSON.stringify(clusters, null, 2) +
        "\nGravity: " + JSON.stringify(gravity, null, 2) + "</pre>";
}

function updateHotspotPanel(hotspotClusters){
    const panel = document.getElementById("hotspotPanel");
    if(!panel) return;
    panel.innerHTML = "";
    Object.entries(hotspotClusters).forEach(function(entry){
        const cid = entry[0];
        const nodes = entry[1];
        const div = document.createElement("div");
        div.innerHTML = "<b>Cluster " + cid + "</b>: " +
            nodes.map(function(n){ return n[0]; }).join(", ");
        panel.appendChild(div);
    });
}

function updateShardPanel(nodeClusters, agentClusters){
    const panel = document.getElementById("shardPanel");
    if(!panel) return;
    panel.innerHTML = "";

    const nodeDiv = document.createElement("div");
    nodeDiv.innerHTML = "<b>Node Shards</b>:<br>";
    Object.entries(nodeClusters).forEach(function(entry){
        const nodeId = entry[0];
        const shardId = entry[1];
        const span = document.createElement("span");
        span.style.color = shardColors[shardId % shardColors.length];
        span.style.marginRight = "4px";
        span.innerText = nodeId.substring(0, 8) + " ";
        nodeDiv.appendChild(span);
    });
    panel.appendChild(nodeDiv);

    const agentDiv = document.createElement("div");
    agentDiv.innerHTML = "<br><b>Agent Shards</b>:<br>";
    Object.entries(agentClusters).forEach(function(entry){
        const agentId = entry[0];
        const shardId = entry[1];
        const span = document.createElement("span");
        span.style.color = agentColors[shardId % agentColors.length];
        span.style.marginRight = "4px";
        span.innerText = agentId + " ";
        agentDiv.appendChild(span);
    });
    panel.appendChild(agentDiv);
}
