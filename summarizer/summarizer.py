class Summarizer:

    def summarize(self, concepts):
        """
        Convert concepts into simple readable summaries
        """

        summaries = []

        for c in concepts["concepts"]:
            name = c["name"]

            # simple rule-based fallback (later replace with LLM)
            summaries.append({
                "concept": name,
                "summary": f"{name} concept explained in simple terms"
            })

        return {"nodes": summaries}