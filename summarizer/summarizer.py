class Summarizer:

    def summarize(self, concepts):
        """
        Generate simple summaries for every topic recursively.
        """

        summaries = []

        self._traverse(concepts["topics"], summaries)

        return {"nodes": summaries}

    def _traverse(self, topics, summaries):
        """
        Recursively traverse the topic hierarchy.
        """

        for topic in topics:

            summaries.append({
                "concept": topic["name"],
                "summary": f"{topic['name']} explained in simple terms."
            })

            self._traverse(topic.get("subtopics", []), summaries)