# runtime/gbrain/ontology_builder.py

from collections import defaultdict


class OntologyBuilder:

    def build(self, graph_nodes):
        """
        基于 cluster + relation + gravity 自动生成层级。

        接受 dict 或对象。
        """
        clusters = defaultdict(list)

        for node_id, node in graph_nodes.items():
            if isinstance(node, dict):
                tags = node.get("tags", [])
            else:
                tags = getattr(node, "metadata", {}).get("tags", [])

            if isinstance(tags, list):
                for tag in tags:
                    if tag and isinstance(tag, str):
                        clusters[tag].append((0.5, node_id))

        ontology = {}
        for tag, nodes_list in clusters.items():
            nodes_list.sort(reverse=True)
            core = [nid for g, nid in nodes_list[:1]]
            secondary = [nid for g, nid in nodes_list[1:]]
            ontology[tag] = {
                "core": core,
                "secondary": secondary,
            }

        return ontology


ontology_builder = OntologyBuilder()
