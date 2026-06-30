import uuid


class TreeBuilder:

    def build(self, hierarchy, summaries=None):

        summary_map = {}

        if summaries:
            summary_map = {
                s["concept"]: s["summary"]
                for s in summaries.get("nodes", [])
            }

        self.visited = set()

        root = {
            "id": str(uuid.uuid4()),
            "label": hierarchy["chapter"],
            "summary": summary_map.get(hierarchy["chapter"], ""),
            "children": []
        }

        nodes = [
            {
                "id": root["id"],
                "label": root["label"],
                "summary": root["summary"]
            }
        ]

        edges = []

        for topic in hierarchy["topics"]:
            child = self._build_recursive(
                topic,
                summary_map,
                nodes,
                edges,
                root["id"]
            )

            if child:
                root["children"].append(child)

        self._validate(root)

        return {
            "chapter": hierarchy["chapter"],
            "root": root,
            "nodes": nodes,
            "edges": edges
        }

    # --------------------------------------------------

    def _build_recursive(
        self,
        topic,
        summary_map,
        nodes,
        edges,
        parent_id
    ):

        name = topic["name"].strip()

        # duplicate node
        if name in self.visited:
            return None

        self.visited.add(name)

        node_id = str(uuid.uuid4())

        node = {
            "id": node_id,
            "label": name,
            "summary": summary_map.get(name, ""),
            "children": []
        }

        nodes.append({
            "id": node_id,
            "label": name,
            "summary": node["summary"]
        })

        edges.append({
            "from": parent_id,
            "to": node_id,
            "type": "Parent-Child"
        })

        for child in topic.get("subtopics", []):

            child_node = self._build_recursive(
                child,
                summary_map,
                nodes,
                edges,
                node_id
            )

            if child_node:
                node["children"].append(child_node)

        return node

    # --------------------------------------------------

    def _validate(self, root):

        ids = set()

        def dfs(node):

            if node["id"] in ids:
                raise ValueError(
                    f"Duplicate node id: {node['id']}"
                )

            ids.add(node["id"])

            if "children" not in node:
                raise ValueError(
                    f"{node['label']} missing children field"
                )

            for child in node["children"]:
                dfs(child)

        dfs(root)