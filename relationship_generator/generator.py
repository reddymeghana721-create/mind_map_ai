import json
import re

from .prompts import RELATIONSHIP_PROMPT


class RelationshipGenerator:

    def __init__(self, llm):
        self.llm = llm

    def generate(self, hierarchy, chapter_text):

        topic_names = self._extract_topics(hierarchy["topics"])

        prompt = (
            RELATIONSHIP_PROMPT
            + "\n\nCHAPTER TEXT\n\n"
            + chapter_text
            + "\n\nHIERARCHY\n\n"
            + json.dumps(hierarchy, indent=2)
        )

        response = self.llm.generate(prompt)

        data = self._safe_json(response)

        return self._validate(data, topic_names)

    # -----------------------------

    def _extract_topics(self, topics):

        names = []

        for topic in topics:
            names.append(topic["name"])
            names.extend(
                self._extract_topics(
                    topic.get("subtopics", [])
                )
            )

        return names

    # -----------------------------

    def _safe_json(self, response):

        try:
            return json.loads(response)

        except:

            match = re.search(r"\{.*\}", response, re.DOTALL)

            if match:

                try:
                    return json.loads(match.group())

                except:
                    return {}

        return {}

    # -----------------------------

    def _validate(self, data, topic_names):

        valid = set(name.lower() for name in topic_names)

        seen = set()

        cleaned = []

        allowed = {
            "Produces",
            "Requires",
            "Uses",
            "Depends On",
            "Related To",
            "Contrasts With",
            "Contains",
            "Occurs Before",
            "Occurs After"
        }

        for rel in data.get("relationships", []):

            source = rel.get("from", "").strip()

            target = rel.get("to", "").strip()

            relation = rel.get("relation", "").strip()

            if source.lower() not in valid:
                continue

            if target.lower() not in valid:
                continue

            if source.lower() == target.lower():
                continue

            if relation not in allowed:
                continue

            key = tuple(sorted([source.lower(), target.lower()])) + (relation,)

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