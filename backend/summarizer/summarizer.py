class Summarizer:

    def __init__(self, llm):
        self.llm = llm

    # ==========================================
    # MAIN
    # ==========================================
    def summarize(self, concepts):

        summaries = []

        self._traverse(
            concepts["topics"],
            summaries,
            chapter=concepts.get("chapter", ""),
            parent=concepts.get("chapter", "")
        )

        return {"nodes": summaries}

    # ==========================================
    # RECURSIVELY TRAVERSE TOPICS
    # ==========================================
    def _traverse(self, topics, summaries, chapter, parent):

        for topic in topics:

            summary = self._generate_summary(
                chapter,
                topic["name"],
                parent
            )

            summaries.append({
                "concept": topic["name"],
                "summary": summary
            })

            self._traverse(
                topic.get("subtopics", []),
                summaries,
                chapter,
                topic["name"]
            )

    # ==========================================
    # GENERATE AI SUMMARY
    # ==========================================
    def _generate_summary(self, chapter, concept, parent):

        prompt = f"""
You are an expert Biology teacher creating educational content for a mind map.

Chapter:
{chapter}

Parent Topic:
{parent}

Concept:
{concept}

Generate information ONLY about this concept.

Return the information EXACTLY in this format:

Definition:
<one short sentence>

Key Points:
- Point 1
- Point 2
- Point 3

Importance:
<one short sentence>

Rules:

- Use ONLY information from the given chapter.
- Keep language suitable for Class 10 students.
- Keep the definition to one sentence.
- Provide exactly 3 key points.
- Each key point should be short.
- Keep importance to one sentence.
- Do NOT add any extra headings.
- Do NOT include markdown.
- Return plain text only.

Example:

Definition:
Process by which green plants prepare food.

Key Points:
- Uses sunlight
- Uses chlorophyll
- Produces glucose

Importance:
Provides food and releases oxygen.
"""

        try:

            response = self.llm.generate(prompt)

            return response.strip()

        except Exception:

            return f"""Definition:
Information unavailable.

Key Points:
- {concept}
- Related to {parent}
- Part of {chapter}

Importance:
An important concept in this chapter."""