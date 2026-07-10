import json
import re

from .prompts import EXPANSION_PROMPT


class ConceptExpander:

    def __init__(self, llm):
        self.llm = llm

    # ==========================================
    # PUBLIC FUNCTION
    # ==========================================
    def expand(self, hierarchy):

        topics = hierarchy.get("topics", [])

        self._expand_topics(
            topics,
            hierarchy.get("chapter", "")
        )

        return hierarchy

    # ==========================================
    # RECURSIVELY EXPAND
    # ==========================================
    def _expand_topics(self, topics, chapter):

        for topic in topics:

            # Expand only if the node has no children
            if not topic.get("subtopics"):

                new_children = self._generate_children(
                    chapter,
                    topic["name"]
                )

                topic["subtopics"] = [
                    {
                        "name": child,
                        "subtopics": []
                    }
                    for child in new_children
                ]

            self._expand_topics(
                topic.get("subtopics", []),
                chapter
            )

    # ==========================================
    # CALL LLM
    # ==========================================
    def _generate_children(self, chapter, concept):

        prompt = f"""
{EXPANSION_PROMPT}

Chapter:
{chapter}

Concept:
{concept}
"""

        try:

            response = self.llm.generate(prompt)

            data = self._safe_json(response)

            return data.get("subconcepts", [])

        except Exception:

            return []

    # ==========================================
    # SAFE JSON
    # ==========================================
    def _safe_json(self, response):

        try:
            return json.loads(response)

        except Exception:

            match = re.search(r"\{.*\}", response, re.DOTALL)

            if match:
                try:
                    return json.loads(match.group())
                except Exception:
                    pass

        return {}