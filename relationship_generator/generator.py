import json
import re
from .prompts import RELATIONSHIP_PROMPT


class RelationshipGenerator:

    def __init__(self, llm):
        self.llm = llm

    def generate(self, concepts):
        """
        Input: list of concepts from Concept Extractor
        Output: validated relationships
        """

        # Step 1: extract only concept names
        concept_names = [c["name"] for c in concepts]

        # Step 2: build prompt input
        prompt = (
            RELATIONSHIP_PROMPT +
            "\n\nConcepts:\n" +
            str(concept_names)
        )

        # Step 3: call LLM
        response = self.llm.generate(prompt)

        # Step 4: safe JSON parsing
        data = self._safe_json_parse(response)

        if "relationships" not in data:
            return {
                "error": "Invalid JSON from LLM",
                "raw_output": response
            }

        # Step 5: validate relationships
        return self._validate(data, concept_names)

    # -------------------------
    # SAFE JSON PARSER
    # -------------------------
    def _safe_json_parse(self, text):
        try:
            return json.loads(text)
        except:
            # extract JSON block from messy output
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    return {}
            return {}

    # -------------------------
    # VALIDATION
    # -------------------------
    def _validate(self, data, concept_names):
        """
        Ensures:
        - no fake concepts
        - only valid relationships
        """

        valid_set = set([c.lower() for c in concept_names])
        valid_relationships = []

        for rel in data.get("relationships", []):
            source = rel.get("from", "").strip()
            target = rel.get("to", "").strip()
            rtype = rel.get("type", "Unknown")

            # only keep valid concepts
            if source.lower() in valid_set and target.lower() in valid_set:
                valid_relationships.append({
                    "from": source,
                    "to": target,
                    "type": rtype
                })

        return {
            "relationships": valid_relationships
        }