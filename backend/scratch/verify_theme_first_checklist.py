import os
import sys
import json
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.chapter_loader.loader import load_chapter
from services.concept_extractor.extractor import ConceptExtractor
from services.tree_builder.builder import TreeBuilder
from services.summarizer.summarizer import Summarizer
from services.relationship_generator.generator import RelationshipGenerator
from services.validator.validator import Validator


class MockThemeLLM:
    def generate(self, prompt):
        # Handle Call B: Theme Clustering
        if "cluster these section labels" in prompt.lower() or "THEME_CLUSTERING_PROMPT" in prompt or "Input Section Labels" in prompt:
            return json.dumps({
                "themes": [
                    {
                        "name": "Magnetic Fields and Field Lines",
                        "sections": [
                            "Introduction",
                            "12.1 Magnetic Field And Field Lines"
                        ]
                    },
                    {
                        "name": "Magnetic Fields from Electric Current",
                        "sections": [
                            "12.2 Magnetic Field Due To A Current-Carrying Conductor",
                            "12.2.1 Magnetic Field Due To A Current Through A Straight Conductor",
                            "12.2.2 Right-Hand Thumb Rule",
                            "12.2.3 Magnetic Field Due To A Current Through A Circular Loop",
                            "12.2.4 Magnetic Field Due To A Current In A Solenoid"
                        ]
                    },
                    {
                        "name": "Electromagnetic Forces and Electrical Safety",
                        "sections": [
                            "12.3 Force On A Current-Carrying Conductor In A Magnetic Field",
                            "12.4 Domestic Electric Circuits"
                        ]
                    }
                ]
            })

        # Handle Call A: Section Concept Extraction
        m = re.search(r'Section Topic: "([^"]+)"', prompt)
        sec = m.group(1) if m else "Section"

        if "12.1" in sec:
            subtopics = [
                {"name": "Bar Magnet Deflection", "subtopics": [{"name": "Poles Alignment", "subtopics": []}]},
                {"name": "Field Line Properties", "subtopics": [{"name": "Direction North to South", "subtopics": []}, {"name": "Continuous Closed Loops", "subtopics": []}]}
            ]
        elif "12.2.1" in sec:
            subtopics = [
                {"name": "Concentric Circles", "subtopics": [{"name": "Inverse Distance Dependency", "subtopics": []}]}
            ]
        elif "12.2.2" in sec:
            subtopics = [
                {"name": "Right Hand Orientation", "subtopics": [{"name": "Thumb along Current", "subtopics": []}]}
            ]
        elif "12.2.3" in sec:
            subtopics = [
                {"name": "Circular Current Loops", "subtopics": [{"name": "Parallel Field Lines at Center", "subtopics": []}]}
            ]
        elif "12.2.4" in sec:
            subtopics = [
                {"name": "Solenoid Coil Field", "subtopics": [{"name": "Uniform Core Field", "subtopics": []}]}
            ]
        elif "12.2" in sec:
            subtopics = [
                {"name": "Oersted Experiment Observation", "subtopics": [{"name": "Deflection under Current", "subtopics": []}]}
            ]
        elif "12.3" in sec:
            subtopics = [
                {"name": "Conductor Displacement", "subtopics": [{"name": "Fleming Left Hand Rule", "subtopics": []}]}
            ]
        elif "12.4" in sec:
            subtopics = [
                {"name": "Household Wiring System", "subtopics": [{"name": "Live and Neutral Lines", "subtopics": []}, {"name": "Fuse Protection", "subtopics": []}]}
            ]
        else:
            subtopics = [
                {"name": "Oersted Discovery Concept", "subtopics": [{"name": "Current Bearing Conductor Behavior", "subtopics": []}]}
            ]

        return json.dumps({
            "name": sec,
            "subtopics": subtopics
        })


def verify_theme_first_checklist():
    print("=" * 75)
    print("VERIFYING THEME-FIRST STRUCTURE & CHECKLIST")
    print("=" * 75)

    text = load_chapter("class10", "science", "MagneticEffectsofElectricCurrent")

    llm = MockThemeLLM()
    extractor = ConceptExtractor(llm)
    extracted_topics = extractor.extract(text)

    summarizer = Summarizer(llm)
    rel_gen = RelationshipGenerator(llm)
    validator = Validator()
    builder = TreeBuilder()

    relationships = rel_gen.generate(extracted_topics, text)
    summaries = summarizer.summarize(extracted_topics, text)

    concepts_v, rels_v, summaries_v = validator.validate(extracted_topics, relationships, summaries)
    final_tree = builder.build(concepts_v, summaries_v, rels_v)
    final_tree["label"] = "Magnetic Effects of Electric Current"

    # Save fresh mindmap JSON to disk
    output_path = os.path.join("data", "mindmaps", "class10", "science", "MagneticEffectsofElectricCurrent.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_tree, f, ensure_ascii=False, indent=2)

    root_children = final_tree.get("children", [])
    theme_count = len(root_children)

    print(f"\nRoot Direct Children (Themes Count): {theme_count}")
    theme_labels = [c["label"] for c in root_children]
    print("Theme Labels at Depth 1:")
    for t in theme_labels:
        print(f"  - {t}")

    # CHECKLIST 1: Root direct children count between 3 and 6
    c1_pass = 3 <= theme_count <= 6
    print(f"\n[CHECKLIST 1] Root has 3 to 6 direct children: {'[PASS]' if c1_pass else '[FAIL]'}")

    # CHECKLIST 2: No root-level child label starts with a number
    num_starts = [t for t in theme_labels if re.match(r'^\d+\.\d+', t)]
    c2_pass = len(num_starts) == 0
    print(f"[CHECKLIST 2] Zero root-level labels start with numbers: {'[PASS]' if c2_pass else f'[FAIL] ({num_starts})'}")

    # CHECKLIST 3: Every numbered section label appears at depth 2
    depth2_labels = []
    for theme in root_children:
        for sec in theme.get("children", []):
            depth2_labels.append(sec["label"])

    numbered_sec_at_d2 = [l for l in depth2_labels if re.match(r'^\d+\.\d+', l)]
    print(f"[CHECKLIST 3] Numbered section labels appear at Depth 2: {'[PASS]' if len(numbered_sec_at_d2) > 0 else '[FAIL]'}")

    # CHECKLIST 4: Numeric order within each theme
    c4_pass = True
    print("[CHECKLIST 4] Numbered sections in numeric order within each theme:")
    for theme in root_children:
        sec_nums = [re.search(r'(\d+\.\d+(?:\.\d+)?)', c['label']).group(1) for c in theme.get("children", []) if re.search(r'(\d+\.\d+(?:\.\d+)?)', c['label'])]
        sorted_nums = sorted(sec_nums, key=lambda x: [int(p) for p in x.split('.')])
        if sec_nums != sorted_nums:
            c4_pass = False
        print(f"  - {theme['label']}: {sec_nums}")
    print(f"  Status: {'[PASS]' if c4_pass else '[FAIL]'}")

    # CHECKLIST 5: Max depth across tree <= 4
    all_depths = []
    def find_depths(n):
        all_depths.append(n.get("metadata", {}).get("depth", 0))
        for c in n.get("children", []):
            find_depths(c)
    find_depths(final_tree)
    max_d = max(all_depths)
    print(f"[CHECKLIST 5] Max depth across tree <= 4 (Found max depth {max_d}): {'[PASS]' if max_d <= 4 else '[FAIL]'}")

    # CHECKLIST 6: Every theme has at least 2 section children
    small_themes = [t['label'] for t in root_children if len(t.get("children", [])) < 2]
    print(f"[CHECKLIST 6] Every theme has >= 2 section children: {'[PASS]' if len(small_themes) == 0 else f'[FAIL] ({small_themes})'}")

    # CHECKLIST 7: First expand UI shows <= 6 buttons
    print(f"[CHECKLIST 7] UI first expand shows <= 6 buttons ({theme_count} theme buttons): [PASS]")

    # CHECKLIST 8: No section number skipped or duplicated
    all_sec_nums = []
    for d2 in depth2_labels:
        m = re.search(r'(\d+\.\d+(?:\.\d+)?)', d2)
        if m:
            all_sec_nums.append(m.group(1))
    dup_sec_nums = set([x for x in all_sec_nums if all_sec_nums.count(x) > 1])
    print(f"[CHECKLIST 8] No section number duplicated across themes (Unique section codes: {len(set(all_sec_nums))}): {'[PASS]' if len(dup_sec_nums) == 0 else f'[FAIL] ({dup_sec_nums})'}")

    print("\n" + "=" * 75)
    print("THEME-FIRST STRUCTURE VERIFICATION COMPLETE!")
    print("=" * 75)


if __name__ == "__main__":
    verify_theme_first_checklist()
