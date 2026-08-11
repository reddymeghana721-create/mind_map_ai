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


class MockSubSectionLLM:
    def generate(self, prompt):
        # Call B: Theme clustering
        if "cluster these section labels" in prompt.lower() or "THEME_CLUSTERING_PROMPT" in prompt:
            return json.dumps({
                "themes": [
                    {
                        "name": "Understanding Chemical Properties of Acids and Bases",
                        "sections": [
                            "2.1 Understanding Chemical Properties Of Acids And Bases",
                            "2.2 What Do All Acids And All Bases Have In Common?"
                        ]
                    },
                    {
                        "name": "Strength of Acid and Base Solutions",
                        "sections": [
                            "2.3 How Strong Are Acid Or Base Solutions?"
                        ]
                    },
                    {
                        "name": "More About Salts and Chemical Derivatives",
                        "sections": [
                            "2.4 More About Salts"
                        ]
                    }
                ]
            })

        # Call A: Section Concept Extraction
        m = re.search(r'Section Topic: "([^"]+)"', prompt)
        sec = m.group(1) if m else "Section"

        if "2.3.1" in sec:
            subtopics = [{"name": "pH in Digestive System", "subtopics": []}, {"name": "pH Cause of Tooth Decay", "subtopics": []}]
        elif "2.3" in sec:
            subtopics = [{"name": "Universal Indicator Scale", "subtopics": []}, {"name": "pH Scale Definition 0 to 14", "subtopics": []}]
        elif "2.4.1" in sec:
            subtopics = [{"name": "Sodium Chloride Salt Family", "subtopics": []}]
        elif "2.4.2" in sec:
            subtopics = [{"name": "Salt Solution Neutrality", "subtopics": []}]
        elif "2.4.3" in sec:
            subtopics = [{"name": "Sodium Hydroxide Chlor-Alkali Process", "subtopics": []}, {"name": "Bleaching Powder Synthesis", "subtopics": []}]
        elif "2.4.4" in sec:
            subtopics = [{"name": "Plaster of Paris Hydration", "subtopics": []}]
        elif "2.4" in sec:
            subtopics = [{"name": "Salts Preparation & Classification", "subtopics": []}]
        elif "2.2.1" in sec:
            subtopics = [{"name": "Do Acids Produce Ions in Water", "video": "/uploads/gen1_notebooklm.mp4", "subtopics": []}]
        elif "2.2" in sec:
            subtopics = [{"name": "Hydrogen Ions Conduction", "subtopics": []}]
        elif "2.1" in sec:
            subtopics = [{"name": "Litmus Indicator Color Change", "subtopics": []}]
        else:
            subtopics = [{"name": "Acid Base Reactions", "subtopics": []}]

        return json.dumps({
            "name": sec,
            "subtopics": subtopics
        })


def verify_nested_subsections():
    print("=" * 75)
    print("VERIFYING SUBSECTION NESTING (2.3.1 under 2.3, 2.4.1 & 2.4.2 under 2.4)")
    print("=" * 75)

    text = load_chapter("class10", "science", "Acids, Bases and Salts")

    llm = MockSubSectionLLM()
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
    final_tree["label"] = "Acids, Bases and Salts"

    # Save to disk
    out_path = os.path.join("data", "mindmaps", "class10", "science", "Acids, Bases and Salts.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_tree, f, ensure_ascii=False, indent=2)

    # Print Tree Structure
    print("\nGenerated Mindmap Hierarchy:")
    def print_node(node, depth=0):
        indent = "  " * depth
        label = node.get("label", "Root")
        print(f"{indent}- [{node.get('type', 'node')}] {label}")
        for child in node.get("children", []):
            print_node(child, depth + 1)

    print_node(final_tree)

    # Verify 2.3.1 under 2.3
    node_2_3 = None
    node_2_4 = None
    def find_nodes(n):
        nonlocal node_2_3, node_2_4
        lbl = n.get("label", "")
        if "2.3 " in lbl or "2.3 How" in lbl:
            node_2_3 = n
        if "2.4 " in lbl or "2.4 More" in lbl:
            node_2_4 = n
        for c in n.get("children", []):
            find_nodes(c)

    find_nodes(final_tree)

    print("\n" + "-" * 75)
    if node_2_3:
        children_2_3 = [c["label"] for c in node_2_3.get("children", [])]
        print(f"Children of 2.3 Node: {children_2_3}")
        has_2_3_1 = any("2.3.1" in c for c in children_2_3)
        print(f"-> 2.3.1 is child of 2.3: {'[PASS]' if has_2_3_1 else '[FAIL]'}")

    if node_2_4:
        children_2_4 = [c["label"] for c in node_2_4.get("children", [])]
        print(f"Children of 2.4 Node: {children_2_4}")
        has_2_4_1 = any("2.4.1" in c for c in children_2_4)
        has_2_4_2 = any("2.4.2" in c for c in children_2_4)
        print(f"-> 2.4.1 & 2.4.2 are children of 2.4: {'[PASS]' if (has_2_4_1 and has_2_4_2) else '[FAIL]'}")

    print("=" * 75)


if __name__ == "__main__":
    verify_nested_subsections()
