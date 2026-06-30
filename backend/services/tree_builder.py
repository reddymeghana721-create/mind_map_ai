class TreeBuilder:
    def build(self, concepts, relationships, summaries):

        summary_map = {s["concept"]: s["summary"] for s in summaries}

        nodes = []
        for c in concepts:
            nodes.append({
                "id": c["name"],
                "type": c["type"],
                "importance": c["importance"],
                "summary": summary_map.get(c["name"], "")
            })

        return {
            "nodes": nodes,
            "edges": relationships
        }