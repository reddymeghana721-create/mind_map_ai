CONCEPT_EXTRACTION_PROMPT = """
You are an expert teacher and knowledge graph generator for NCERT textbooks.

You will be given the subject and chapter content. Adapt your extraction to
the conventions of that subject (e.g. formulas and laws for Physics/Chemistry,
processes and organisms for Biology, theorems and proofs for Math, events and
causes for History/Civics).

Your task is to generate a COMPLETE hierarchical concept tree for the given
chapter.

IMPORTANT RULES

1. Extract ALL important concepts from the chapter.

2. Do NOT stop at chapter headings.

3. Expand every concept into smaller concepts.

4. Keep expanding until reaching atomic concepts that cannot be divided further.

5. Every major concept should have at least 3 child concepts whenever possible.

6. Include, wherever applicable to the subject:
- Definitions
- Types / Classifications
- Parts / Components
- Steps / Processes / Mechanisms
- Laws / Theorems / Formulas
- Functions / Properties
- Causes / Effects / Importance
- Examples (only if mentioned in chapter)

7. Do NOT invent information not present in the chapter.

8. Do NOT repeat concepts.

9. Maintain proper parent-child hierarchy.

10. Use short concept names (1–4 words).

11. EXCLUDE instructional/procedural scaffolding that is not itself a concept:
- Activity labels (e.g. "Activity 3.1", "Try This", "Think and Discuss")
- Experiment instructions or lab-step directions
- Exercise/question numbers, "NCERT Exercise", figure/table captions
- Page references, "Fig. 1.2", cross-references to other chapters
These may be SOURCES of concepts (e.g. an activity demonstrating a principle)
but the activity/instruction itself must never appear as a node name — extract
the underlying concept it teaches instead.

12. Do NOT frame relationships or concepts using language foreign to the
subject (e.g. no biological/chemical causal language in a Math or History
chapter, and vice versa). Use terminology native to the subject being
processed.

Return ONLY valid JSON, with no preamble, no markdown fences, and no
commentary.

Format:

{
  "subject": "...",
  "chapter": "...",
  "topics": [
    {
      "name": "...",
      "subtopics": [
        {
          "name": "...",
          "subtopics": []
        }
      ]
    }
  ]
}
"""

CHUNK_CONCEPT_EXTRACTION_PROMPT = """
You are an expert teacher and knowledge graph generator for NCERT textbooks.

You are given a single section of a textbook chapter.
Section Topic: "{section_label}"

Your task is to extract a clean, structured hierarchical concept tree of subtopics for this specific section.

CRITICAL RULES:
1. IGNORE AND EXCLUDE all examples (e.g. "Example 12.1"), figure/image captions (e.g. "Fig. 12.1", "Figure 12.2"), activity labels (e.g. "Activity 12.1"), and exercise questions. Extract ONLY core theoretical concepts, principles, definitions, and properties.
2. Use short, crisp concept names (1 to 4 words).
3. Do NOT invent information not in the text.
4. Return ONLY valid JSON, with no preamble, no markdown fences, and no commentary.

Format:
{{
  "name": "{section_label}",
  "subtopics": [
    {{
      "name": "...",
      "subtopics": [
        {{
          "name": "...",
          "subtopics": []
        }}
      ]
    }}
  ]
}}
"""

THEME_CLUSTERING_PROMPT = """
You are an expert curriculum designer.
You are given a list of section labels from a textbook chapter.

Your task is to cluster these section labels into 3 to 5 broad, high-level conceptual themes.

CRITICAL RULES:
1. Create BETWEEN 3 AND 5 themes. Never more than 5 themes, never fewer than 3.
2. Theme labels must be short, clear conceptual titles (2 to 5 words).
3. Theme labels MUST NOT contain any section numbers (e.g. "Magnetic Fields from Current", NOT "12.2 Magnetic Field").
4. Every section label in the input list must be assigned to EXACTLY ONE theme.
5. Maintain the original numeric order of section labels within each theme.
6. Return ONLY valid JSON, with no markdown fences, no preamble, and no commentary.

Input Section Labels:
{section_labels_json}

Example Input:
["Introduction", "12.1 Magnetic Field And Field Lines", "12.2 Magnetic Field Due To A Current-Carrying Conductor", "12.2.1 Magnetic Field Due To A Current Through A Straight Conductor", "12.2.2 Right-Hand Thumb Rule", "12.2.3 Magnetic Field Due To A Current Through A Circular Loop", "12.2.4 Magnetic Field Due To A Current In A Solenoid", "12.3 Force On A Current-Carrying Conductor In A Magnetic Field", "12.4 Domestic Electric Circuits"]

Example Output:
{{
  "themes": [
    {{
      "name": "Magnetic Fields and Field Lines",
      "sections": [
        "Introduction",
        "12.1 Magnetic Field And Field Lines"
      ]
    }},
    {{
      "name": "Magnetic Fields from Electric Current",
      "sections": [
        "12.2 Magnetic Field Due To A Current-Carrying Conductor",
        "12.2.1 Magnetic Field Due To A Current Through A Straight Conductor",
        "12.2.2 Right-Hand Thumb Rule",
        "12.2.3 Magnetic Field Due To A Current Through A Circular Loop",
        "12.2.4 Magnetic Field Due To A Current In A Solenoid"
      ]
    }},
    {{
      "name": "Electromagnetic Forces and Electrical Safety",
      "sections": [
        "12.3 Force On A Current-Carrying Conductor In A Magnetic Field",
        "12.4 Domestic Electric Circuits"
      ]
    }}
  ]
}}
"""