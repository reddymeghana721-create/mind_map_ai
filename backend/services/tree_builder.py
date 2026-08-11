import uuid


class TreeBuilder:

    def build(self, hierarchy, summaries, relationships=None):
        summary_map = self._build_summary_map(summaries)

        tree = {
            "id": self._new_id(),
            "type": "chapter",
            "label": hierarchy.get("chapter", "Unknown Chapter"),
            "summary": summary_map.get(hierarchy.get("chapter", ""), ""),
            "preview": self._get_preview(
                summary_map.get(hierarchy.get("chapter", ""), "")
            ),
            "ui": {
                "expandable": True,
                "visual_type": "root"
            },
            "children": self._build_nodes(
                hierarchy.get("topics", []),
                summary_map,
                current_depth=1
            ),
            "relationships": (
                relationships.get("relationships", [])
                if relationships
                else []
            )
        }

        return tree

    def _build_nodes(self, nodes, summary_map, current_depth=1):
        result = []

        for node in nodes:
            label = node.get("name", "Unknown")

            children = self._build_nodes(
                node.get("subtopics", []),
                summary_map,
                current_depth=current_depth + 1
            )

            summary = summary_map.get(
                label,
                f"Textbook Excerpt:\n{label} provides key theoretical information."
            )

            result.append({
                "id": self._new_id(),
                "type": self._infer_type(current_depth),
                "label": label,
                "summary": summary,
                "preview": self._get_preview(summary),
                "keywords": self._extract_keywords(summary),
                "ui": self._build_ui(label, children),
                "children": children,
                "metadata": {
                    "depth": current_depth,
                    "leaf": len(children) == 0
                }
            })

        return result

    def _build_summary_map(self, summaries):
        summary_map = {}
        for item in summaries.get("nodes", []):
            summary_map[item["concept"]] = item["summary"]
        return summary_map

    def _build_ui(self, label, children):
        return {
            "expandable": len(children) > 0,
            "visual_type": self._get_visual_type(label, children),
            "node_style": "default",
            "animation_hint": self._get_animation_hint(children),
            "icon": self._get_icon(label)
        }

    def _infer_type(self, depth):
        if depth == 1:
            return "theme"
        elif depth == 2:
            return "section"
        return "concept"

    def _get_visual_type(self, label, children):
        if len(children) == 0:
            return "text_node"
        return "tree_node"

    def _get_animation_hint(self, children):
        if len(children) == 0:
            return "fade_in"
        if len(children) > 3:
            return "expand_cascade"
        return "expand_simple"

    def _get_icon(self, label):
        label_lower = label.lower()
        if "photo" in label_lower or "sun" in label_lower:
            return "sun"
        if "respir" in label_lower or "bolt" in label_lower or "electric" in label_lower:
            return "bolt"
        if "nutrition" in label_lower or "apple" in label_lower:
            return "apple"
        if "excretion" in label_lower or "filter" in label_lower:
            return "filter"
        return "circle"

    def _get_preview(self, summary):
        if not summary:
            return ""
        if len(summary) <= 60:
            return summary
        return summary[:60] + "..."

    def _extract_keywords(self, summary):
        if not summary:
            return []
        words = summary.split()
        keywords = []
        for word in words:
            word = word.strip(".,()")
            if len(word) > 6:
                keywords.append(word)
        return keywords[:5]

    def _new_id(self):
        return str(uuid.uuid4())
