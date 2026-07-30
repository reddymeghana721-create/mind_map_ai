import json
import re

from .relationship_prompts import RELATIONSHIP_PROMPT


class RelationshipGenerator:

    def __init__(self, llm):
        self.llm = llm

    def generate(self, hierarchy, chapter_text):

        topic_names = self._extract_topics(hierarchy.get("topics", []))

        # Truncate chapter text to 2500 chars to stay well within LLM prompt token limits
        trimmed_text = chapter_text[:2500] if len(chapter_text) > 2500 else chapter_text

        prompt = (
            RELATIONSHIP_PROMPT
            + "\n\nCHAPTER TEXT SUMMARY:\n"
            + trimmed_text
            + "\n\nHIERARCHY:\n"
            + json.dumps(hierarchy, indent=2)
        )

        response = self.llm.generate(prompt)

        data = self._safe_json(response)

        result = self._validate(data, topic_names)

        if not result["relationships"]:
            result["relationships"] = self._fallback(topic_names)

        return result

    def _extract_topics(self, topics):

        names = []

        for topic in topics:
            names.append(topic.get("name", ""))

            names.extend(
                self._extract_topics(topic.get("subtopics", []))
            )

        return names

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

    def _normalize(self, text):
        return text.lower().strip()

    def _validate(self, data, topic_names):

        valid = {self._normalize(n) for n in topic_names if n}

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

    def _fallback(self, topic_names):

        valid_topics = [t for t in topic_names if t]
        if len(valid_topics) < 2:
            return []

        relationships = []

        for i in range(len(valid_topics) - 1):
            relationships.append({
                "from": valid_topics[i],
                "to": valid_topics[i + 1],
                "relation": "Related To"
            })

        return relationships
