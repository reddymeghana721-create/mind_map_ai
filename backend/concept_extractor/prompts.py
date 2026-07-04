CONCEPT_PROMPT = """
You are an expert NCERT textbook analyzer and educational curriculum designer.

Your task is to extract the COMPLETE concept hierarchy from the given chapter.

Return ONLY valid JSON in the format:

{
    "chapter": "Chapter Name",
    "topics": [
        {
            "name": "Topic",
            "subtopics": [
                {
                    "name": "Subtopic",
                    "subtopics": []
                }
            ]
        }
    ]
}

=========================
STRICT RULES
=========================

1. Extract ONLY concepts that actually appear in the chapter.

2. Preserve the textbook hierarchy.

3. Do NOT invent concepts.

4. Do NOT skip important concepts.

5. Continue recursively until the smallest meaningful concept.

6. Every node MUST contain:
   - name
   - subtopics

7. Leaf concepts must have:
   "subtopics": []

8. Do NOT generate duplicate concepts anywhere.

9. Every concept name must be unique.

10. Keep concept names short (1-4 words whenever possible).

11. Convert question headings into concept names.

Examples

"What are Life Processes?"
→ "Life Processes"

"How do Plants Obtain Nutrition?"
→ "Plant Nutrition"

"Transportation in Human Beings"
→ "Human Transportation"

"Transportation in Plants"
→ "Plant Transportation"

"Excretion in Human Beings"
→ "Human Excretion"

12. Do NOT use textbook sentences as concept names.

13. Do NOT create artificial grouping nodes such as

"Types of Respiration"

unless the textbook explicitly uses that heading.

Correct:

Respiration
 ├── Aerobic Respiration
 └── Anaerobic Respiration

14. Prefer actual biological concepts over body systems.

Correct:

Human Transportation
 ├── Blood
 ├── Plasma
 ├── RBC
 ├── WBC
 ├── Platelets
 ├── Heart
 ├── Blood Vessels
 └── Lymph

NOT

Human Transportation
 └── Respiratory System

15. For plant transportation, extract concepts like

Plant Transportation
 ├── Xylem
 ├── Phloem
 ├── Transpiration
 └── Translocation

instead of generic names like
"Water Transport"
or
"Food Transport"

unless those are the actual textbook headings.

16. Prefer scientific concepts over descriptive headings.

17. Do NOT create vague concepts such as

Energy Requirements

Maintenance Functions

Sources

Introduction

Overview

Background

unless they are actual section headings.

18. Keep siblings at the same level of abstraction.

Bad:

Nutrition
 ├── Photosynthesis
 ├── Plant
 └── Digestion

Good:

Nutrition
 ├── Autotrophic Nutrition
 └── Heterotrophic Nutrition

19. The output should represent the chapter outline, NOT a concept map.

20. Return ONLY JSON.

No markdown.

No explanation.

No comments.

The output must be directly parsable by Python json.loads().
"""