import json
import re
from .concept_prompts import CONCEPT_EXTRACTION_PROMPT


class ConceptExtractor:

    def __init__(self, llm):
        self.llm = llm
        self.seen = set()

    def extract_section_headings(self, text: str):
        """
        Scans text for numbered section headings (e.g. '12.1 MAGNETIC FIELD AND FIELD LINES',
        '12.2.1 Magnetic Field...'), explicitly filtering out Figures, Examples, Activities,
        Questions, and Tables.
        """
        lines = text.split("\n")
        EXCLUDE_KEYWORDS = [
            "figure", "fig.", "fig", "example", "ex.", "ex ", "activity",
            "question", "questions", "table", "reprint", "ncert", "act."
        ]
        headings = []

        for i, line in enumerate(lines):
            s = line.strip()
            if not s:
                continue

            m = re.match(r'^(\d+(?:\.\d+)+|\d+\.\d+)\s+(.+)$', s)
            if m:
                num, title = m.group(1), m.group(2).strip()

                lower_line = s.lower()
                lower_title = title.lower()

                if any(lower_line.startswith(ex) or lower_title.startswith(ex) for ex in EXCLUDE_KEYWORDS):
                    continue

                if i + 1 < len(lines):
                    nxt = lines[i + 1].strip()
                    if (
                        nxt
                        and not re.match(r'^\d+(\.\d+)*\s', nxt)
                        and not any(nxt.lower().startswith(ex) for ex in EXCLUDE_KEYWORDS)
                        and len(nxt) <= 45
                        and not nxt.endswith(('.', '?', '!', ':'))
                        and nxt[0].isupper()
                    ):
                        title = title + " " + nxt

                headings.append({
                    "line_idx": i,
                    "number": num,
                    "title": title
                })

        return headings

    def build_section_context(self, text: str, max_chars_per_section=800):
        """
        Splits chapter text by section headers and builds a structured section-by-section context
        so that EVERY section (e.g. 12.1, 12.2, 12.3, 12.4) gets equal representation in the LLM prompt.
        """
        lines = text.split("\n")
        EXCLUDE_KEYWORDS = [
            "figure", "fig.", "fig", "example", "ex.", "ex ", "activity",
            "question", "questions", "table", "reprint", "ncert", "act."
        ]
        headings = self.extract_section_headings(text)

        if not headings:
            return text[:4500]

        context_parts = []
        for idx in range(len(headings)):
            h = headings[idx]
            line_idx = h["line_idx"]
            num = h["number"]
            title = h["title"]

            next_line_idx = headings[idx + 1]["line_idx"] if idx + 1 < len(headings) else len(lines)
            sec_lines = lines[line_idx + 1:next_line_idx]

            filtered_lines = [
                l.strip() for l in sec_lines
                if l.strip() and not any(l.strip().lower().startswith(ex) for ex in EXCLUDE_KEYWORDS)
            ]
            sec_content = " ".join(filtered_lines)[:max_chars_per_section]

            context_parts.append(f"=== SECTION {num}: {title} ===\n{sec_content}\n")

        return "\n".join(context_parts)

    def normalize(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'[^a-z0-9\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text

    def deduplicate_tree(self, node):

        if not isinstance(node, dict):
            return None

        name = node.get("name") or node.get("chapter")
        if name:
            key = self.normalize(name)

            if key in self.seen:
                return None

            self.seen.add(key)

        children = node.get("subtopics", [])
        new_children = []

        for child in children:
            cleaned = self.deduplicate_tree(child)
            if cleaned:
                new_children.append(cleaned)

        node["subtopics"] = new_children
        return node

    def extract(self, text: str):
        # 1. Build section-by-section context (equal coverage across all sections 12.1..12.4)
        section_context = self.build_section_context(text)

        # 2. Build full prompt
        prompt = CONCEPT_EXTRACTION_PROMPT + "\n\nChapter Content by Sections:\n" + section_context

        # 3. Call LLM
        response = self.llm.generate(prompt)

        # 4. Safe JSON extraction
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if not match:
            return {"concepts": []}

        cleaned = match.group()

        try:
            data = json.loads(cleaned)

            self.seen = set()  # reset per chapter
            cleaned_data = self.deduplicate_tree(data)

            return cleaned_data

        except Exception:
            return {"concepts": []}
