RELATIONSHIP_PROMPT = """
You are an expert knowledge graph generator.

You MUST generate relationships between topics in a school textbook chapter.

INPUT:
- Chapter text
- Hierarchical topic structure

TASK:
Generate meaningful relationships between DIFFERENT topics.

IMPORTANT RULES:
- Use ONLY topic names from the hierarchy
- DO NOT return empty relationships
- ALWAYS try to generate at least 8–15 relationships if possible
- Prefer connecting leaf nodes
- Avoid duplicates
- Focus on biological/causal relationships

Allowed relations:
Produces, Requires, Uses, Depends On, Leads To, Enables, Causes, Transports, Occurs In, Part Of, Supports, Contains

OUTPUT FORMAT:
{
  "relationships": [
    {
      "from": "Topic A",
      "to": "Topic B",
      "relation": "Uses"
    }
  ]
}
"""
