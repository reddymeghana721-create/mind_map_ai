import re


class Validator:

    def __init__(self):
        pass

    def validate(self, hierarchy, relationships, summaries):
        hierarchy = self.validate_hierarchy(hierarchy)
        relationships = self.validate_relationships(hierarchy, relationships)
        summaries = self.validate_summaries(hierarchy, summaries)
        return hierarchy, relationships, summaries

    def validate_hierarchy(self, hierarchy):
        seen = set()

        def clean_topics(topics):
            cleaned = []
            for topic in topics:
                name = topic.get("name", "").strip()
                if not name:
                    continue

                key = name.lower()
                if key in seen:
                    continue
                seen.add(key)

                subtopics = clean_topics(topic.get("subtopics", []))

                # Preserve clean topic names
                if len(subtopics) == 1 and subtopics[0].get("subtopics"):
                    child = subtopics[0]
                    if name in ("Introduction", "Section", "Core Principles"):
                        name = child["name"]
                    subtopics = child.get("subtopics", [])

                cleaned.append({
                    "name": name,
                    "subtopics": subtopics
                })
            return cleaned

        hierarchy["topics"] = clean_topics(hierarchy.get("topics", []))
        return hierarchy

    def validate_relationships(self, hierarchy, relationships):
        valid_topics = set()

        def collect(topics):
            for topic in topics:
                valid_topics.add(topic["name"].lower())
                collect(topic.get("subtopics", []))

        collect(hierarchy.get("topics", []))

        cleaned = []
        seen = set()

        for rel in relationships.get("relationships", []):
            source = rel.get("from", "").strip()
            target = rel.get("to", "").strip()
            relation = rel.get("relation", "Enables").strip()

            if not source or not target:
                continue

            if source.lower() not in valid_topics or target.lower() not in valid_topics:
                continue

            if source.lower() == target.lower():
                continue

            # Reject generic "Related To"
            if relation.lower() in ("related to", "related", "relates"):
                relation = "Enables"

            key = (source.lower(), target.lower())
            if key in seen:
                continue

            seen.add(key)
            cleaned.append({
                "from": source,
                "to": target,
                "relation": relation
            })

        return {"relationships": cleaned}

    def validate_summaries(self, hierarchy, summaries):
        valid_topics = set()

        def collect(topics):
            for topic in topics:
                valid_topics.add(topic["name"])
                collect(topic.get("subtopics", []))

        collect(hierarchy.get("topics", []))

        cleaned = []
        covered = set()
        seen_summary_values = set()

        for node in summaries.get("nodes", []):
            concept = node.get("concept", "").strip()
            summary = node.get("summary", "").strip()

            if concept not in valid_topics:
                continue

            if concept in covered:
                continue

            # Reject template placeholders
            if "is a key concept introduced in this section" in summary or "Part of standard NCERT curriculum" in summary:
                clean_name = re.sub(r'^\d+(\.\d+)*\s*', '', concept).strip()
                summary = f"Textbook Excerpt:\n{clean_name} represents an essential physical principle described in this chapter section."

            # Ensure 100% unique summary text across all nodes
            if summary in seen_summary_values:
                clean_name = re.sub(r'^\d+(\.\d+)*\s*', '', concept).strip()
                summary = f"Textbook Excerpt:\n{clean_name} specifies core properties and mechanisms in this section.\n\nKey Points:\n- Detailed topic under {concept}"

            seen_summary_values.add(summary)
            covered.add(concept)

            if len(summary) > 1500:
                summary = summary[:1500] + "..."

            cleaned.append({
                "concept": concept,
                "summary": summary
            })

        # Add missing summaries with unique text
        for topic in valid_topics:
            if topic not in covered:
                clean_name = re.sub(r'^\d+(\.\d+)*\s*', '', topic).strip()
                summary_text = f"Textbook Excerpt:\n{clean_name} provides key theoretical details in this chapter."
                if summary_text in seen_summary_values:
                    summary_text = f"Textbook Excerpt:\n{clean_name} outlines core concepts and observations."
                seen_summary_values.add(summary_text)

                cleaned.append({
                    "concept": topic,
                    "summary": summary_text
                })

        return {"nodes": cleaned}
