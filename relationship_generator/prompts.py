RELATIONSHIP_PROMPT = """
You are an expert educational knowledge graph generator.

You are given:

1. The complete chapter text.
2. The hierarchical topic structure extracted from the chapter.

The hierarchy already defines ALL parent-child relationships.

Your task is ONLY to identify meaningful semantic relationships
between topics that belong to DIFFERENT branches of the hierarchy.

Return ONLY valid JSON in the following format:

{
    "relationships": [
        {
            "from": "Topic A",
            "to": "Topic B",
            "relation": "Produces | Requires | Uses | Depends On | Related To | Contrasts With | Contains | Occurs Before | Occurs After"
        }
    ]
}

STRICT RULES

- DO NOT generate parent-child relationships.
- DO NOT connect a topic to its own ancestor or descendant.
- DO NOT invent new topics.
- ONLY use topic names present in the hierarchy.
- ONLY create relationships explicitly supported by the chapter text.
- If uncertain, DO NOT create the relationship.
- Generate at most ONE relationship between any pair of topics.
- Maximum 10 relationships.
- Prefer relationships between LEAF topics (topics without subtopics).
- Ignore organizational headings unless they have a meaningful semantic relationship.

Return ONLY valid JSON.

No markdown.
No explanations.
"""