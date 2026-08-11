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


class FastLLM:
    def generate(self, prompt):
        return ""


def run_fast_generation(chapter_filename, display_name):
    print(f"\n=======================================================")
    print(f"Generating mindmap for {display_name}...")
    print(f"=======================================================")

    text = load_chapter("class10", "science", chapter_filename)

    llm = FastLLM()
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
    final_tree["label"] = display_name

    # Attach video for Do Acids Produce Ions in Water if present
    def attach_video(node):
        if "Do Acids Produce Ions in Water" in node.get("label", ""):
            node["video"] = "/uploads/gen1_notebooklm.mp4"
            if "ui" in node:
                node["ui"]["has_video"] = True
        for c in node.get("children", []):
            attach_video(c)

    attach_video(final_tree)

    # Save mindmap JSON
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "mindmaps", "class10", "science")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{chapter_filename}.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_tree, f, ensure_ascii=False, indent=2)

    print(f"Saved: {out_path}")

    # Print Tree
    def print_node(node, depth=0):
        indent = "  " * depth
        print(f"{indent}- [{node.get('type')}] {node.get('label')}")
        for c in node.get("children", []):
            print_node(c, depth + 1)

    print("\nHierarchy Tree:")
    print_node(final_tree)


if __name__ == "__main__":
    run_fast_generation("Acids, Bases and Salts", "Acids, Bases and Salts")
    run_fast_generation("MagneticEffectsofElectricCurrent", "Magnetic Effects of Electric Current")
