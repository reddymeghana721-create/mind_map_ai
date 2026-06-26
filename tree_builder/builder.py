class TreeBuilder:

    def build(self, concepts, relationships, summaries):

        # STEP 1: safety normalization
        if isinstance(relationships, dict):
            relationships = relationships.get("relationships", [])

        if isinstance(relationships, str):
            import json
            try:
                relationships = json.loads(relationships)
            except:
                relationships = []

        tree = {
            "nodes": [],
            "edges": []
        }

        # STEP 2: build concept map (for summaries)
        summary_map = {
            s["concept"]: s["summary"]
            for s in summaries
        }

        # STEP 3: create nodes
        for c in concepts:
            tree["nodes"].append({
                "id": c["name"],
                "type": c.get("type", "unknown"),
                "importance": c.get("importance", 1),
                "summary": summary_map.get(c["name"], "")
            })

        # STEP 4: create edges (FIX IS HERE)
        for rel in relationships:

            # 🛑 safeguard AGAIN
            if not isinstance(rel, dict):
                continue

            parent = rel.get("from")
            child = rel.get("to")
            rtype = rel.get("type", "unknown")

            if parent and child:
                tree["edges"].append({
                    "from": parent,
                    "to": child,
                    "type": rtype
                })

        return tree