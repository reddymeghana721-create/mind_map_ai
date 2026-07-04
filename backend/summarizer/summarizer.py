class Summarizer:

    def __init__(self, llm):
        self.llm = llm

    def summarize(self, concepts):
        """
        Generate AI summaries for every topic recursively.
        """

        summaries = []

        self._traverse(
            concepts["topics"],
            summaries,
            chapter=concepts.get("chapter", ""),
            parent=concepts.get("chapter", "")
        )

        return {"nodes": summaries}

    # --------------------------------------------------

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

    # --------------------------------------------------

    def _generate_summary(self, chapter, concept, parent):

        prompt = f"""
You are an expert school textbook teacher.

Chapter:
{chapter}

Parent Topic:
{parent}

Concept:
{concept}

Write a SHORT educational summary.

Rules:
- The summary MUST be based ONLY on the given chapter.
- Never use meanings from other fields or everyday life.
- Explain what the concept means in this chapter.
- Mention why it is important.
- Use simple language suitable for Class 10 students.
- Keep it between 20 and 35 words.
- Do NOT start with the concept name.
- Do NOT write phrases like "This concept...", "The concept...", or "explained in simple terms."
- Return ONLY the summary.

Example:
Concept: Photosynthesis
Output:
The process by which green plants prepare food using sunlight, carbon dioxide, and water. It provides energy for plant growth and releases oxygen essential for life.
"""

        try:
            response = self.llm.generate(prompt)
            return response.strip()

        except Exception:
            return f"An important concept in {chapter}."