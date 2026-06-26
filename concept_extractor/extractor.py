import json
import re
from .prompts import CONCEPT_PROMPT


class ConceptExtractor:

    def __init__(self, llm):
        self.llm = llm

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
            return data
        except:
            return {"concepts": []}