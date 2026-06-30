import json

class ConceptExtractor:
    def __init__(self, llm):
        self.llm = llm

    def extract(self, text):
        prompt = f"""
Extract key concepts from this text.

Return ONLY JSON:
{{
  "concepts": [
    {{"name": "", "type": "", "importance": 1}}
  ]
}}

TEXT:
{text}
"""
        response = self.llm.generate(prompt)

        return json.loads(response)