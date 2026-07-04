import uuid


class TreeBuilder:

    def build(self, hierarchy, summaries, relationships=None):

        summary_map = self._build_summary_map(summaries)

        tree = {
            "id": self._new_id(),
            "type": "chapter",
            "label": hierarchy.get("chapter", "Unknown Chapter"),
            "summary": summary_map.get(hierarchy.get("chapter", ""), ""),
            "ui": {
                "expandable": True,
                "visual_type": "root"
            },
            "children": self._build_nodes(
                hierarchy.get("topics", []),
                summary_map
            ),
            "relationships": (
                relationships.get("relationships", [])
                if relationships
                else []
            )
        }

        return tree

    # --------------------------------------------------

    def _build_nodes(self, nodes, summary_map):

        result = []

        for node in nodes:

            label = node.get("name", "Unknown")

            children = self._build_nodes(
                node.get("subtopics", []),
                summary_map
            )

            result.append({
                "id": self._new_id(),
                "type": self._infer_type(children),
                "label": label,
                "summary": summary_map.get(label, ""),
                "ui": self._build_ui(label, children),
                "children": children,
                "metadata": {
                    "depth": self._calculate_depth(children),
                    "leaf": len(children) == 0
                }
            })

        return result

    # --------------------------------------------------

    def _build_summary_map(self, summaries):

        summary_map = {}

        for item in summaries.get("nodes", []):
            summary_map[item["concept"]] = item["summary"]

        return summary_map

    # --------------------------------------------------

    def _build_ui(self, label, children):

        return {
            "expandable": len(children) > 0,
            "visual_type": self._get_visual_type(label, children),
            "node_style": "default",
            "animation_hint": self._get_animation_hint(children),
            "icon": self._get_icon(label)
        }

    # --------------------------------------------------

    def _infer_type(self, children):
        # Keep node type consistent.
        return "concept"

    # --------------------------------------------------

    def _get_visual_type(self, label, children):

        label_lower = label.lower()

        if "photosynthesis" in label_lower:
            return "process_flow"

        if "respiration" in label_lower:
            return "energy_cycle"

        if "transport" in label_lower:
            return "system_flow"

        if len(children) == 0:
            return "text_node"

        return "tree_node"

    # --------------------------------------------------

    def _get_animation_hint(self, children):

        if len(children) == 0:
            return "fade_in"

        if len(children) > 3:
            return "expand_cascade"

        return "expand_simple"

    # --------------------------------------------------

    def _get_icon(self, label):

        label_lower = label.lower()

        if "photo" in label_lower:
            return "sun"

        if "respir" in label_lower:
            return "bolt"

        if "nutrition" in label_lower:
            return "apple"

        if "excretion" in label_lower:
            return "filter"

        return "circle"

    # --------------------------------------------------

    def _calculate_depth(self, children):

        if not children:
            return 0

        return 1 + max(
            [child["metadata"]["depth"] for child in children],
            default=0
        )

    # --------------------------------------------------

    def _new_id(self):

        return str(uuid.uuid4())