import json
import re
from .prompts import CONCEPT_PROMPT


class ConceptExtractor:

    def __init__(self, llm):
        self.llm = llm
        self.seen = set()   # ✅ ADD THIS

    def normalize(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'[^a-z0-9\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text

    def deduplicate_tree(self, node):
        """
        Removes duplicate concepts recursively
        """
        if not isinstance(node, dict):
            return None

        name = node.get("name") or node.get("chapter")
        if name:
            key = self.normalize(name)

            if key in self.seen:
                return None

            self.seen.add(key)

        # process children recursively
        children = node.get("subtopics", [])
        new_children = []

        for child in children:
            cleaned = self.deduplicate_tree(child)
            if cleaned:
                new_children.append(cleaned)

        node["subtopics"] = new_children
        return node

    def extract(self, text):
        prompt = CONCEPT_PROMPT + "\n\nChapter Text:\n" + text

        response = self.llm.generate(prompt)

        # safe JSON extraction
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if not match:
            return {"concepts": []}

        cleaned = match.group()

        try:
            data = json.loads(cleaned)

            # ✅ APPLY DEDUP CLEANING HERE
            self.seen = set()  # reset per chapter
            cleaned_data = self.deduplicate_tree(data)

            return cleaned_data

        except:
            return {"concepts": []}