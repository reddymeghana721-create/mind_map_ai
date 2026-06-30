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

        return self._validate(data, topic_names)

    # ---------------------------------------------------
    # RECURSIVELY EXTRACT ALL TOPIC NAMES
    # ---------------------------------------------------
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
    # VALIDATE TOPIC
    # ---------------------------------------------------
    def _is_valid_topic(self, name, valid_topics):
        return self._normalize(name) in valid_topics

    # ---------------------------------------------------
    # CLEAN OUTPUT
    # ---------------------------------------------------
    def _validate(self, data, topic_names):

        valid_topics = {
            self._normalize(name)
            for name in topic_names
        }

        allowed_relations = {

            "Produces",
            "Consumes",
            "Uses",
            "Requires",
            "Carries",
            "Contains",
            "Transports",
            "Filters",
            "Absorbs",
            "Releases",
            "Converts To",
            "Occurs In",
            "Part Of",
            "Pumps",
            "Flows Through",
            "Supports",
            "Enables"

        }

        seen = set()

        cleaned = []

        for rel in data.get("relationships", []):

            source = rel.get("from", "").strip()
            target = rel.get("to", "").strip()
            relation = rel.get("relation", "").strip()

            if not source or not target:
                continue

            if source == target:
                continue

            if not self._is_valid_topic(source, valid_topics):
                continue

            if not self._is_valid_topic(target, valid_topics):
                continue

            if relation not in allowed_relations:
                continue

            # prevent duplicate direction
            key = (
                self._normalize(source),
                self._normalize(target),
                relation
            )

            reverse_key = (
                self._normalize(target),
                self._normalize(source),
                relation
            )

            if key in seen or reverse_key in seen:
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