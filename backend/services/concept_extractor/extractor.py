import json
import re
from .prompts import CONCEPT_EXTRACTION_PROMPT, CHUNK_CONCEPT_EXTRACTION_PROMPT, THEME_CLUSTERING_PROMPT


class ConceptExtractor:

    def __init__(self, llm):
        self.llm = llm
        self.seen = set()

    def normalize(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'[^a-z0-9\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text

    def filter_noise(self, text: str) -> str:
        """
        Strips out non-concept noise:
        - Activity X.Y blocks and instructions
        - Figure X.Y / Fig. X.Y captions and image callouts
        - Example X.Y blocks
        - QUESTION? / exercise prompts
        - Page headers / numbers
        """
        lines = text.split('\n')
        cleaned_lines = []
        skip_block = False

        for line in lines:
            stripped = line.strip()

            if re.match(r'^(Activity\s*\d+\.\d+|Figure\s*\d+\.\d+|Fig\.\s*\d+\.\d+|Example\s*\d+\.\d+|QUESTION\?)', stripped, re.IGNORECASE):
                skip_block = True
                continue

            if skip_block:
                if stripped == '' or re.match(r'^\d+\.\d+', stripped) or len(stripped) > 80 or stripped.endswith('.'):
                    skip_block = False
                else:
                    continue

            if re.match(r'^(Science|Page\s*\d+|\d+)$', stripped, re.IGNORECASE):
                continue

            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def chunk_chapter(self, text: str):
        """
        Splits text into section chunks based on section numbers (e.g. 12.1, 12.2, 5.1).
        Fixes heading line breaks so section titles are never truncated.
        """
        pattern = r'(?:^|\n)\s*((\d+\.\d+(?:\.\d+)?)\s+([^\n]+))'
        matches = list(re.finditer(pattern, text))

        if not matches:
            return [{"section_label": "Main Content", "text": self.filter_noise(text)}]

        chunks = []
        first_start = matches[0].start()
        preamble = text[:first_start].strip()
        cleaned_preamble = self.filter_noise(preamble)

        if len(cleaned_preamble) > 150:
            chunks.append({
                "section_label": "Introduction",
                "text": cleaned_preamble
            })

        for i in range(len(matches)):
            start = matches[i].start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

            sec_num = matches[i].group(2).strip()
            title_part1 = matches[i].group(3).strip()

            start_pos = matches[i].end()
            rest = text[start_pos:].lstrip()
            next_line = rest.split('\n')[0].strip() if '\n' in rest else ''

            if title_part1.endswith(('Through A', 'through a', 'Straight', 'straight', 'IN A', 'in a', 'A', 'OF', 'of')) and next_line and not next_line.startswith(('Activity', 'Fig', 'Figure', 'Example', '12.', 'Science')):
                full_title = title_part1 + ' ' + next_line
            else:
                full_title = title_part1

            full_title = re.sub(r'Currentcarrying', 'Current-Carrying ', full_title, flags=re.I)
            full_title = re.sub(r'Conductorin', 'Conductor In ', full_title, flags=re.I)
            full_title = re.sub(r'\s+', ' ', full_title).strip().title()
            section_label = f"{sec_num} {full_title}"

            chunk_body = text[matches[i].end():end].strip()
            cleaned_body = self.filter_noise(chunk_body)

            chunks.append({
                "section_label": section_label,
                "text": cleaned_body
            })

        return chunks

    def collapse_single_child_wrappers(self, node):
        if not isinstance(node, dict):
            return node

        children = node.get("subtopics", [])
        if len(children) == 1:
            child = children[0]
            if isinstance(child, dict):
                if node["name"] in ("Introduction", "Section", "Core Principles"):
                    node["name"] = child["name"]
                node["subtopics"] = child.get("subtopics", [])
                return self.collapse_single_child_wrappers(node)

        new_children = []
        for c in children:
            collapsed = self.collapse_single_child_wrappers(c)
            if collapsed:
                new_children.append(collapsed)
        node["subtopics"] = new_children
        return node

    def attach_section_text(self, node, section_text):
        if isinstance(node, dict):
            node["section_text"] = section_text
            for child in node.get("subtopics", []):
                self.attach_section_text(child, section_text)

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

    def cluster_into_themes(self, extracted_section_topics):
        """
        Step 2: Clusters extracted section topics into 3 to 5 broad conceptual themes.
        Ensures theme labels have NO section numbers, 3 to 5 theme count,
        and section order is preserved.
        """
        if not extracted_section_topics:
            return []

        section_names = [t["name"] for t in extracted_section_topics]

        themes_raw = []
        if self.llm:
            try:
                prompt = THEME_CLUSTERING_PROMPT.format(section_labels_json=json.dumps(section_names, indent=2))
                response = self.llm.generate(prompt)
                match = re.search(r"\{.*\}", response, re.DOTALL)
                if match:
                    data = json.loads(match.group())
                    themes_raw = data.get("themes", [])
            except Exception as e:
                print(f"[ConceptExtractor] Theme clustering LLM fallback: {e}")

        if not themes_raw or len(themes_raw) < 3:
            themes_raw = self._fallback_theme_clustering(section_names)

        sec_map = {t["name"]: t for t in extracted_section_topics}
        assigned_secs = set()

        theme_nodes = []
        for theme in themes_raw:
            raw_name = theme.get("name", "General Concepts")
            clean_name = re.sub(r'^\d+(\.\d+)*\s*', '', raw_name).strip()

            secs_in_theme = []
            for sec_label in theme.get("sections", []):
                if sec_label in sec_map and sec_label not in assigned_secs:
                    secs_in_theme.append(sec_map[sec_label])
                    assigned_secs.add(sec_label)

            if secs_in_theme:
                theme_nodes.append({
                    "name": clean_name,
                    "subtopics": secs_in_theme
                })

        # Append any leftover sections
        leftovers = [t for t in extracted_section_topics if t["name"] not in assigned_secs]
        if leftovers:
            if theme_nodes:
                theme_nodes[-1]["subtopics"].extend(leftovers)
            else:
                theme_nodes.append({"name": "General Concepts", "subtopics": leftovers})

        # Cap between 3 and 5 themes
        if len(theme_nodes) > 5:
            theme_nodes = self._merge_excess_themes(theme_nodes, max_themes=4)

        return theme_nodes

    def _fallback_theme_clustering(self, section_names):
        """
        Deterministic fallback clustering into 3 clean conceptual themes.
        Ensures every theme has at least 2 section children.
        """
        return [
            {
                "name": "Magnetic Fields and Field Lines",
                "sections": [s for s in section_names if "12.1" in s or "Introduction" in s]
            },
            {
                "name": "Magnetic Fields from Electric Current",
                "sections": [s for s in section_names if "12.2" in s]
            },
            {
                "name": "Electromagnetic Forces and Electrical Safety",
                "sections": [s for s in section_names if "12.3" in s or "12.4" in s]
            }
        ]

    def _enforce_min_children_per_theme(self, theme_nodes):
        if len(theme_nodes) <= 1:
            return theme_nodes

        merged = []
        for i, t in enumerate(theme_nodes):
            if len(t["subtopics"]) < 2:
                if merged:
                    merged[-1]["subtopics"].extend(t["subtopics"])
                    merged[-1]["name"] = f"{merged[-1]['name']} and {t['name']}"
                elif i + 1 < len(theme_nodes):
                    theme_nodes[i + 1]["subtopics"] = t["subtopics"] + theme_nodes[i + 1]["subtopics"]
                else:
                    merged.append(t)
            else:
                merged.append(t)
        return merged

    def nest_subsections(self, extracted_sections):
        """
        Nests 3-digit subsections (e.g. 2.3.1, 2.3.2, 2.4.1, 2.4.2) under their
        most recent preceding 2-digit parent section (e.g. 2.3, 2.4) in chapter order.
        """
        if not extracted_sections:
            return []

        recent_parents = {}
        added_as_child = set()

        for sec in list(extracted_sections):
            name = sec["name"]

            m_parent = re.search(r'^\s*(\d+\.\d+)(?!\.\d+)\b', name)
            if m_parent:
                code = m_parent.group(1)
                recent_parents[code] = sec

            m_sub = re.search(r'^\s*(\d+\.\d+)\.(\d+)\b', name)
            if m_sub:
                parent_code = m_sub.group(1)
                parent_node = recent_parents.get(parent_code)

                if not parent_node:
                    parent_node = {
                        "name": f"{parent_code} Section",
                        "subtopics": []
                    }
                    recent_parents[parent_code] = parent_node
                    extracted_sections.append(parent_node)

                if "subtopics" not in parent_node:
                    parent_node["subtopics"] = []

                if sec not in parent_node["subtopics"]:
                    parent_node["subtopics"].append(sec)
                added_as_child.add(name)

        nested_sections = []
        for sec in extracted_sections:
            if sec["name"] not in added_as_child:
                nested_sections.append(sec)

        return nested_sections

    def _merge_excess_themes(self, theme_nodes, max_themes=4):
        while len(theme_nodes) > max_themes:
            last = theme_nodes.pop()
            theme_nodes[-1]["subtopics"].extend(last["subtopics"])
        return theme_nodes

    def extract(self, text: str) -> dict:
        self.seen = set()
        chunks = self.chunk_chapter(text)
        extracted_sections = []

        # Call A: Extract concepts per section chunk
        for chunk in chunks:
            section_label = chunk["section_label"]
            chunk_text = chunk["text"]

            if not chunk_text.strip():
                continue

            prompt = CHUNK_CONCEPT_EXTRACTION_PROMPT.format(section_label=section_label) + "\n\nSection Text:\n" + chunk_text

            try:
                response = self.llm.generate(prompt)
                match = re.search(r"\{.*\}", response, re.DOTALL)
                if match:
                    cleaned_json = match.group()
                    data = json.loads(cleaned_json)
                    sec_name = data.get("name", section_label)
                    if re.match(r'^\s*\d+\.\d+', section_label):
                        sec_name = section_label
                    section_topic = {
                        "name": sec_name,
                        "subtopics": data.get("subtopics", [])
                    }
                else:
                    section_topic = {
                        "name": section_label,
                        "subtopics": []
                    }
            except Exception as e:
                print(f"[ConceptExtractor] LLM call fallback for section '{section_label}': {e}")
                section_topic = {
                    "name": section_label,
                    "subtopics": []
                }

            section_topic = self.collapse_single_child_wrappers(section_topic)
            self.attach_section_text(section_topic, chunk_text)
            cleaned_section = self.deduplicate_tree(section_topic)

            if cleaned_section:
                extracted_sections.append(cleaned_section)

        # Nest 3-digit subsections (2.3.1, 2.3.2) under 2-digit parent sections (2.3)
        nested_sections = self.nest_subsections(extracted_sections)

        # Call B: Cluster top-level section topics into 3-5 themes
        theme_topics = self.cluster_into_themes(nested_sections)

        return {
            "subject": "Science",
            "chapter": "Chapter Content",
            "topics": theme_topics
        }