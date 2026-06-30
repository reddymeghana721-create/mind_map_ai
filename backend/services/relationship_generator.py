import json

class RelationshipGenerator:
    def __init__(self, llm):
        self.llm = llm

    def generate(self, concepts):
        prompt = f"""
Create relationships between these concepts:

{concepts}

Return ONLY JSON:
{{
  "relationships": [
    {{"from": "", "to": "", "type": ""}}
  ]
}}
"""

        response = self.llm.generate(prompt)
        return json.loads(response)