class Validator:

    def __init__(self):
        pass

    # ==========================================
    # MAIN VALIDATION FUNCTION
    # ==========================================
    def validate(self, hierarchy, relationships, summaries):

        hierarchy = self.validate_hierarchy(hierarchy)

        relationships = self.validate_relationships(
            hierarchy,
            relationships
        )

        summaries = self.validate_summaries(
            hierarchy,
            summaries
        )

        return hierarchy, relationships, summaries

    # ==========================================
    # HIERARCHY VALIDATION
    # ==========================================
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

                cleaned.append({
                    "name": name,
                    "subtopics": clean_topics(
                        topic.get("subtopics", [])
                    )
                })

            return cleaned

        hierarchy["topics"] = clean_topics(
            hierarchy.get("topics", [])
        )

        return hierarchy

    # ==========================================
    # RELATIONSHIP VALIDATION
    # ==========================================
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
            relation = rel.get("relation", "").strip()

            if not source or not target:
                continue

            if source.lower() not in valid_topics:
                continue

            if target.lower() not in valid_topics:
                continue

            if source.lower() == target.lower():
                continue

            key = (
                source.lower(),
                target.lower(),
                relation.lower()
            )

            if key in seen:
                continue

            seen.add(key)

            cleaned.append({
                "from": source,
                "to": target,
                "relation": relation
            })

        return {
            "relationships": cleaned
        }

    # ==========================================
    # SUMMARY VALIDATION
    # ==========================================
    def validate_summaries(self, hierarchy, summaries):

        valid_topics = set()

        def collect(topics):

            for topic in topics:

                valid_topics.add(topic["name"])

                collect(topic.get("subtopics", []))

        collect(hierarchy.get("topics", []))

        cleaned = []
        covered = set()

        for node in summaries.get("nodes", []):

            concept = node.get("concept", "").strip()
            summary = node.get("summary", "").strip()

            if concept not in valid_topics:
                continue

            if concept in covered:
                continue

            covered.add(concept)

            if not summary:
                summary = f"{concept} is an important concept in this chapter."

            if len(summary) > 250:
                summary = summary[:250] + "..."

            cleaned.append({
                "concept": concept,
                "summary": summary
            })

        # Add missing summaries
        for topic in valid_topics:

            if topic not in covered:

                cleaned.append({
                    "concept": topic,
                    "summary": f"{topic} is an important concept in this chapter."
                })

        return {
            "nodes": cleaned
        }