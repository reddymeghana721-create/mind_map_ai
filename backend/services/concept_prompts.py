CONCEPT_EXTRACTION_PROMPT = """
You are an expert teacher and knowledge graph generator for school textbooks (NCERT).

You are provided with Section-by-Section textbook content organized under section headers (e.g., Section 12.1, Section 12.2, Section 12.3, Section 12.4).

Your task is to generate a COMPLETE, BALANCED, and HIGHLY GRANULAR hierarchical concept tree.

CRITICAL MANDATORY RULES:

1. EVERY SECTION MUST BE EXPANDED:
   - You MUST extract top-level topics corresponding to EVERY main section provided (e.g. 12.1, 12.2, 12.3, 12.4).
   - NEVER leave any main section empty or unexpanded!
   - For Sections like '12.3 Force on a Current Carrying Conductor in a Magnetic Field' and '12.4 Domestic Electric Circuits', you MUST extract at least 3–5 granular subtopics (e.g. Fleming's Left-Hand Rule, Electric Motor, Fuse, Live/Neutral/Earth Wires, Overloading/Short Circuit).

2. MULTI-LEVEL SUBTOPIC EXPANSION:
   - Expand every section into 2nd-level subtopics, and expand major subtopics further into 3rd-level subtopics.
   - Every top-level topic MUST have at least 2–4 child subtopics.

3. EXCLUSIONS (CRITICAL):
   - Do NOT include figure labels, figure numbers, or figure captions (e.g. "Fig. 12.1", "Figure 12.2").
   - Do NOT include example numbers or problem solutions (e.g. "Example 12.1").
   - Do NOT include activity labels or experiment directions (e.g. "Activity 12.1", "Try This").
   - Do NOT include question numbers or exercise headings (e.g. "Question 1", "NCERT Exercise").
   Extract ONLY the core SCIENTIFIC / EDUCATIONAL CONCEPTS taught in those sections.

4. NAMING & HIERARCHY:
   - Use clean, short concept names (2 to 5 words).
   - Remove section numbers like '12.1' or ALL-CAPS formatting from node names.
   - Do NOT repeat concept names within the tree.

Return ONLY valid JSON, with no preamble, no markdown fences, and no commentary.

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
