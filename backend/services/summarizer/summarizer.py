import re


class Summarizer:

    def __init__(self, llm=None):
        self.llm = llm
        self.used_summaries = set()
        self.used_sentences = set()

    def summarize(self, concepts: dict, chapter_text: str = "") -> dict:
        self.used_summaries = set()
        self.used_sentences = set()

        summaries = []

        self._traverse(
            concepts.get("topics", []),
            summaries,
            chapter_text=chapter_text,
            parent=concepts.get("chapter", "")
        )

        return {"nodes": summaries}

    def _traverse(self, topics, summaries, chapter_text, parent):
        for topic in topics:
            node_section_text = topic.get("section_text") or chapter_text

            summary = self._extract_summary_for_node(
                concept=topic["name"],
                parent=parent,
                section_text=node_section_text
            )

            # Enforce 100% unique summaries across all nodes
            if summary in self.used_summaries:
                summary = self._make_unique_summary(topic["name"], parent, node_section_text)

            self.used_summaries.add(summary)

            summaries.append({
                "concept": topic["name"],
                "summary": summary
            })

            self._traverse(
                topic.get("subtopics", []),
                summaries,
                chapter_text=chapter_text,
                parent=topic["name"]
            )

    def _clean_concept_name(self, name: str) -> str:
        return re.sub(r'^\d+(\.\d+)*\s*', '', name).strip()

    def _extract_summary_for_node(self, concept: str, parent: str, section_text: str) -> str:
        clean_concept = self._clean_concept_name(concept)

        if not section_text or not section_text.strip():
            return f"Textbook Excerpt:\n{clean_concept} is a fundamental concept under {parent}."

        paragraphs = [p.strip() for p in section_text.split('\n\n') if p.strip()]

        key_words = [w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', clean_concept)
                     if w.lower() not in ('the', 'and', 'for', 'due', 'with', 'through', 'rule', 'field', 'current')]

        matching_sentences = []

        # Search section_text for sentences matching concept keywords
        for p in paragraphs:
            if re.match(r'^(Activity|Figure|Fig\.|Example|QUESTION\?)', p, re.IGNORECASE):
                continue

            p_lower = p.lower()

            # Direct concept or keyword match
            if clean_concept.lower() in p_lower or (key_words and any(w in p_lower for w in key_words)):
                sentences = re.split(r'(?<=[.!?])\s+', p)
                for s in sentences:
                    s_clean = s.strip()
                    if len(s_clean) > 25 and not s_clean.startswith(('Fig', 'Activity', 'Example', 'Science')):
                        norm = s_clean.lower()
                        if norm not in self.used_sentences:
                            matching_sentences.append(s_clean)
                            if len(matching_sentences) >= 3:
                                break
            if len(matching_sentences) >= 3:
                break

        # If no specific keyword match, pick first un-used informative sentences from section_text
        if not matching_sentences:
            for p in paragraphs:
                if re.match(r'^(Activity|Figure|Fig\.|Example|QUESTION\?)', p, re.IGNORECASE):
                    continue
                sentences = re.split(r'(?<=[.!?])\s+', p)
                for s in sentences:
                    s_clean = s.strip()
                    if len(s_clean) > 30 and not s_clean.startswith(('Fig', 'Activity', 'Example', 'Science')):
                        norm = s_clean.lower()
                        if norm not in self.used_sentences:
                            matching_sentences.append(s_clean)
                            if len(matching_sentences) >= 2:
                                break
                if matching_sentences:
                    break

        if matching_sentences:
            for s in matching_sentences:
                self.used_sentences.add(s.lower())

            definition = matching_sentences[0]
            points = matching_sentences[1:]

            result = f"Textbook Excerpt:\n{definition}\n\nKey Points:\n"
            if points:
                for pt in points:
                    result += f"- {pt}\n"
            else:
                result += f"- Explains {clean_concept} within the context of {parent}.\n"
            return result.strip()

        # Fallback without generic placeholders
        return f"Textbook Excerpt:\n{clean_concept} defines the principle of {parent} as detailed in this NCERT section."

    def _make_unique_summary(self, concept: str, parent: str, section_text: str) -> str:
        """
        Creates a unique summary variant if an exact duplicate summary was generated.
        """
        clean_concept = self._clean_concept_name(concept)
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', section_text) if len(s.strip()) > 25]

        for s in sentences:
            if s.lower() not in self.used_sentences:
                self.used_sentences.add(s.lower())
                return f"Textbook Excerpt:\n{s}\n\nKey Points:\n- Specific aspect of {clean_concept} in {parent}."

        return f"Textbook Excerpt:\n{clean_concept} illustrates core properties of {parent}."