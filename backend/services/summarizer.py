import json
import re


class Summarizer:

    def __init__(self, llm):
        self.llm = llm

    def summarize(self, concepts):
        all_nodes = []
        self._collect_nodes(
            concepts.get("topics", []),
            all_nodes,
            chapter=concepts.get("chapter", "Science"),
            parent=concepts.get("chapter", "Science")
        )

        if not all_nodes:
            return {"nodes": []}

        # Batch summarization in a single LLM request
        concept_list_str = "\n".join([f"- Concept: '{item['concept']}' (Parent: '{item['parent']}')" for item in all_nodes])

        prompt = f"""
You are an expert science teacher creating concise educational summaries for mind map nodes.

Chapter: {concepts.get('chapter', 'Science')}

Concepts to summarize:
{concept_list_str}

For EACH concept above, generate a concise summary strictly formatted as:
Definition: <1 short sentence>
Key Points:
- Point 1
- Point 2
- Point 3
Importance: <1 short sentence>

Return ONLY a valid JSON object with key "nodes":
{{
  "nodes": [
    {{
      "concept": "<Exact Concept Name>",
      "summary": "Definition: ...\\n\\nKey Points:\\n- ...\\n\\nImportance: ..."
    }}
  ]
}}
"""

        try:
            response = self.llm.generate(prompt, max_tokens=1800)
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                data = json.loads(match.group())
                nodes = data.get("nodes", [])
                if nodes:
                    return {"nodes": nodes}
        except Exception as e:
            print(f"Batch summarizer exception: {e}")

        # Fallback if batch LLM fails
        fallback_nodes = []
        for item in all_nodes:
            concept = item["concept"]
            parent = item["parent"]
            fallback_nodes.append({
                "concept": concept,
                "summary": f"Definition:\n{concept} is a fundamental concept.\n\nKey Points:\n- Relates to {parent}\n- Important component\n- Core textbook topic\n\nImportance:\nEssential for understanding."
            })

        return {"nodes": fallback_nodes}

    def _collect_nodes(self, topics, all_nodes, chapter, parent):
        for topic in topics:
            all_nodes.append({
                "concept": topic["name"],
                "parent": parent,
                "chapter": chapter
            })
            self._collect_nodes(
                topic.get("subtopics", []),
                all_nodes,
                chapter,
                topic["name"]
            )
