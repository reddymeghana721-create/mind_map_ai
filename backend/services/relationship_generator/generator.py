import json
import re

from .prompts import RELATIONSHIP_PROMPT


class RelationshipGenerator:

    def __init__(self, llm):
        self.llm = llm

    # ---------------------------------------------------
    # MAIN
    # ---------------------------------------------------
    def generate(self, hierarchy, chapter_text):

        topic_names = self._extract_topics(hierarchy["topics"])

        prompt = (
            RELATIONSHIP_PROMPT
            + "\n\nCHAPTER TEXT:\n"
            + chapter_text
            + "\n\nHIERARCHY:\n"
            + json.dumps(hierarchy, indent=2)
        )

        response = self.llm.generate(prompt)

        data = self._safe_json(response)

        result = self._validate(data, topic_names)

        # 🔥 FALLBACK (ensures graph is never empty)
        if not result["relationships"]:
            result["relationships"] = self._fallback(topic_names)

        return result

    # ---------------------------------------------------
    # EXTRACT TOPICS
    # ---------------------------------------------------
    def _extract_topics(self, topics):

        names = []

        for topic in topics:
            names.append(topic["name"])

            names.extend(
                self._extract_topics(topic.get("subtopics", []))
            )

        return names

    # ---------------------------------------------------
    # SAFE JSON PARSER
    # ---------------------------------------------------
    def _safe_json(self, response):

        if not response:
            return {}

        try:
            return json.loads(response)

        except Exception:
            match = re.search(r"\{.*\}", response, re.DOTALL)

            if match:
                try:
                    return json.loads(match.group())
                except Exception:
                    return {}

        return {}

    # ---------------------------------------------------
    # NORMALIZE
    # ---------------------------------------------------
    def _normalize(self, text):
        return text.lower().strip()

    # ---------------------------------------------------
    # VALIDATE OUTPUT
    # ---------------------------------------------------
    def _validate(self, data, topic_names):

        valid = {self._normalize(n) for n in topic_names}

        cleaned = []
        seen = set()

        for rel in data.get("relationships", []):

            source = rel.get("from", "").strip()
            target = rel.get("to", "").strip()
            relation = rel.get("relation", "Related To").strip()

            if not source or not target:
                continue

            if self._normalize(source) not in valid:
                continue

            if self._normalize(target) not in valid:
                continue

            key = (source, target)

            if key in seen:
                continue

            seen.add(key)

            cleaned.append({
                "from": source,
                "to": target,
                "relation": relation
            })

        return {"relationships": cleaned}

    # ---------------------------------------------------
    # FALLBACK (IMPORTANT)
    # ---------------------------------------------------
    def _fallback(self, topic_names):
        """
        Creates basic linear relationships so graph is never empty.
        """

        if len(topic_names) < 2:
            return []

        relationships = []

        for i in range(len(topic_names) - 1):
            relationships.append({
                "from": topic_names[i],
                "to": topic_names[i + 1],
                "relation": "Related To"
            })

        return relationships