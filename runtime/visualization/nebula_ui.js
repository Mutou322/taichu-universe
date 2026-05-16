// runtime/visualization/nebula_ui.js
// Phase 9 — Nebula UI Visualization

ws.onmessage = function(event){
    const data = JSON.parse(event.data);

    if(data.type === "evolution"){
        updateEvolutionPanel(data);
    }
    if(data.type === "attention_map"){
        updateAttentionMap(data);
    }
    if(data.type === "gbrain"){
        updateGBrainPanel(data);
    }
};

function updateEvolutionPanel(evolution){
    const panel = document.getElementById("evolutionPanel");
    if(!panel) return;
    const div = document.createElement("div");
    div.innerHTML = "<b>Gen " + evolution.generation + "</b> " +
        "Fitness: " + Math.max.apply(null, evolution.fitness_results) + " " +
        "Genome: " + JSON.stringify(evolution.best_genome);
    panel.appendChild(div);
    panel.scrollTop = panel.scrollHeight;
}

function updateAttentionMap(attention){
    Object.entries(attention).forEach(function(entry){
        var node = entry[0];
        var weight = entry[1];
        var n = network.body.nodes[node];
        if(n){
            n.color = "rgb(" + Math.min(255, Math.floor(weight * 50)) + "," +
                (255 - Math.floor(weight * 50)) + ",100)";
        }
    });
    network.redraw();
}

function updateGBrainPanel(gbrain){
    const panel = document.getElementById("gbrainPanel");
    if(!panel) return;
    panel.innerHTML = "<pre>Clusters: " + JSON.stringify(gbrain.clusters, null, 2) +
        "\nGravity: " + JSON.stringify(gbrain.gravity, null, 2) + "</pre>";
}
