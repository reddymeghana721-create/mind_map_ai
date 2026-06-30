import json

class Summarizer:
    def __init__(self, llm):
        self.llm = llm

    def summarize(self, concepts):
        prompt = f"""
Summarize each concept in one simple line.

Return ONLY JSON:
{{
  "nodes": [
    {{"concept": "", "summary": ""}}
  ]
}}

Concepts:
{concepts}
"""

        response = self.llm.generate(prompt)
        return json.loads(response)