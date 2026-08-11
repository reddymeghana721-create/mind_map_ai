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
from services.llm.client import OpenRouterLLM


def build_mindmap_for_chapter(class_name, subject, chapter_name):
    print(f"\nBuilding mindmap for {class_name} / {subject} / {chapter_name}...")
    
    text = load_chapter(class_name, subject, chapter_name)

    llm = OpenRouterLLM()
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
    final_tree["label"] = chapter_name.replace("_", " ")

    # Ensure video is attached to "Do Acids Produce Ions in Water" if present
    def attach_video_if_target(node):
        if "Do Acids Produce Ions in Water" in node.get("label", ""):
            node["video"] = "/uploads/gen1_notebooklm.mp4"
            if "ui" in node:
                node["ui"]["has_video"] = True
        for c in node.get("children", []):
            attach_video_if_target(c)

    attach_video_if_target(final_tree)

    # Save mindmap JSON
    out_dir = os.path.join("data", "mindmaps", class_name, subject)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{chapter_name}.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_tree, f, ensure_ascii=False, indent=2)

    print(f"Saved {out_path} cleanly!")

    # Print Tree Hierarchy
    def print_tree(node, depth=0):
        indent = "  " * depth
        print(f"{indent}- [{node.get('type')}] {node.get('label')}")
        for c in node.get("children", []):
            print_tree(c, depth + 1)

    print("\nGenerated Tree Structure:")
    print_tree(final_tree)


if __name__ == "__main__":
    build_mindmap_for_chapter("class10", "science", "Acids, Bases and Salts")
    build_mindmap_for_chapter("class10", "science", "MagneticEffectsofElectricCurrent")
