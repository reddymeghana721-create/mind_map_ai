import json
import re

from .relationship_prompts import RELATIONSHIP_PROMPT


class RelationshipGenerator:

    def __init__(self, llm):
        self.llm = llm

    def generate(self, hierarchy, chapter_text):
        topic_names = self._extract_topics(hierarchy.get("topics", []))

        prompt = (
            RELATIONSHIP_PROMPT
            + "\n\nCHAPTER TEXT:\n"
            + chapter_text[:4000]
            + "\n\nHIERARCHY:\n"
            + json.dumps(hierarchy, indent=2)
        )

        try:
            response = self.llm.generate(prompt)
            data = self._safe_json(response)
            result = self._validate(data, topic_names)

            if len(result["relationships"]) >= 5:
                return result
        except Exception as e:
            print(f"[RelationshipGenerator] LLM failed: {e}")

        # Structured, domain-accurate branch relationships
        return {"relationships": self._generate_structured_relationships(hierarchy.get("topics", []))}

    def _extract_topics(self, topics):
        names = []
        for topic in topics:
            names.append(topic.get("name", ""))
            names.extend(self._extract_topics(topic.get("subtopics", [])))
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
            relation = rel.get("relation", "Enables").strip()

            if not source or not target:
                continue
            if self._normalize(source) not in valid:
                continue
            if self._normalize(target) not in valid:
                continue
            if self._normalize(source) == self._normalize(target):
                continue

            # Reject generic "Related To"
            if relation.lower() in ("related to", "related", "relates"):
                relation = self._infer_relation(source, target)

            key = (self._normalize(source), self._normalize(target))
            if key in seen:
                continue

            seen.add(key)
            cleaned.append({
                "from": source,
                "to": target,
                "relation": relation
            })

        return {"relationships": cleaned}

    def _infer_relation(self, source, target):
        s_low = source.lower()
        t_low = target.lower()

        if "rule" in s_low or "rule" in t_low or "direction" in t_low:
            return "Determined By"
        if "current" in s_low and "field" in t_low:
            return "Produces"
        if "force" in t_low or "force" in s_low:
            return "Exerts"
        if "fuse" in s_low or "earth" in s_low or "protect" in t_low:
            return "Protects Against"
        if "solenoid" in s_low or "core" in t_low:
            return "Enables"
        if "distance" in t_low or "proportional" in t_low:
            return "Proportional To"

        return "Enables"

    def _generate_structured_relationships(self, topics):
        relationships = []
        seen = set()

        for topic in topics:
            parent_name = topic.get("name", "")
            subtopics = topic.get("subtopics", [])

            for sub in subtopics:
                sub_name = sub.get("name", "")
                rel_type = self._infer_relation(parent_name, sub_name)

                key = (self._normalize(parent_name), self._normalize(sub_name))
                if key not in seen:
                    seen.add(key)
                    relationships.append({
                        "from": parent_name,
                        "to": sub_name,
                        "relation": rel_type
                    })

                children = sub.get("subtopics", [])
                for child in children:
                    child_name = child.get("name", "")
                    child_rel = self._infer_relation(sub_name, child_name)
                    c_key = (self._normalize(sub_name), self._normalize(child_name))
                    if c_key not in seen:
                        seen.add(c_key)
                        relationships.append({
                            "from": sub_name,
                            "to": child_name,
                            "relation": child_rel
                        })

        return relationships
