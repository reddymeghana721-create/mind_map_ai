import json


class GraphExporter:

    def export(self, tree, relationships):
        nodes = []
        edges = []

        self._build_nodes(tree, nodes)
        self._build_edges(relationships, edges)

        graph = {
            "nodes": nodes,
            "edges": edges
        }

        with open("graph.json", "w", encoding="utf-8") as f:
            json.dump(graph, f, indent=4, ensure_ascii=False)

        return graph

    # ------------------------

    def _build_nodes(self, node, nodes):

        nodes.append({
            "data": {
                "id": node["id"],
                "label": node["label"],
                "type": node.get("type", "concept")
            }
        })

        for child in node.get("children", []):
            self._build_nodes(child, nodes)

    # ------------------------

    def _build_edges(self, relationships, edges):

        for rel in relationships.get("relationships", []):
            edges.append({
                "data": {
                    "source": rel["from"],
                    "target": rel["to"],
                    "label": rel.get("relation", "")
                }
            })