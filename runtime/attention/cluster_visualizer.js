// runtime/attention/cluster_visualizer.js
// Nebula UI — Cluster Visualization for Phase 6 Week 5

function visualizeClusters(network, nodeClusters, agentClusters) {
    // nodeClusters: {node_id: cluster_id}
    // agentClusters: {agent_id: cluster_id}

    Object.entries(nodeClusters).forEach(function(entry) {
        const nodeId = entry[0];
        const clusterId = entry[1];
        const node = network.body.nodes[nodeId];
        if (node) {
            node.color = clusterColors[clusterId % clusterColors.length];
            node.size = 20 + clusterId * 3;
        }
    });

    Object.entries(agentClusters).forEach(function(entry) {
        const agentId = entry[0];
        const clusterId = entry[1];
        const agentNode = network.body.nodes[agentId];
        if (agentNode) {
            agentNode.color = agentColors[clusterId % agentColors.length];
        }
    });

    network.redraw();
}

const clusterColors = ["#ff3300", "#33ff33", "#3366ff", "#ffcc00"];
const agentColors = ["#cc33ff", "#33ffcc", "#ff9933", "#6699ff"];
