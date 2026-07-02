import json

from chapter_loader.loader import load_chapter
from concept_extractor.extractor import ConceptExtractor
from relationship_generator.generator import RelationshipGenerator
from summarizer.summarizer import Summarizer
from tree_builder.builder import TreeBuilder
from llm.client import OpenRouterLLM
from exporter import GraphExporter


llm = OpenRouterLLM()

# =========================
# STEP 1: LOAD CHAPTER
# =========================
text = load_chapter(
    class_name="class10",
    subject="science",
    chapter="life_processes"
)

# =========================
# STEP 2: CONCEPT EXTRACTION
# =========================
concept_extractor = ConceptExtractor(llm)
concepts = concept_extractor.extract(text)

print("\n===== CONCEPTS =====\n")
print(json.dumps(concepts, indent=4, ensure_ascii=False))


# =========================
# STEP 3: RELATIONSHIPS
# =========================
relationship_generator = RelationshipGenerator(llm)

relationships = relationship_generator.generate(
    hierarchy=concepts,
    chapter_text=text
)

print("\n===== RELATIONSHIPS =====\n")
print(json.dumps(relationships, indent=4, ensure_ascii=False))


# =========================
# STEP 4: SUMMARIZATION
# =========================
summarizer = Summarizer(llm)

summaries = summarizer.summarize(concepts)

print("\n===== SUMMARIES =====\n")
print(json.dumps(summaries, indent=4, ensure_ascii=False))


# =========================
# STEP 5: TREE BUILDING
# =========================
tree_builder = TreeBuilder()

final_tree = tree_builder.build(
    hierarchy=concepts,
    summaries=summaries
)

print("\n===== FINAL TREE =====\n")
print(json.dumps(final_tree, indent=4, ensure_ascii=False))


# =========================
# STEP 6: GRAPH EXPORT (UI READY)
# =========================
exporter = GraphExporter()

graph = exporter.export(
    tree=final_tree,
    relationships=relationships
)

print("\n===== GRAPH SAVED =====")
print("File: graph.json created successfully 🚀")