from flask import json

from backend.services import summarizer
from chapter_loader.loader import load_chapter
from concept_extractor.extractor import ConceptExtractor
from relationship_generator.generator import RelationshipGenerator
from summarizer.summarizer import Summarizer
from tree_builder.builder import TreeBuilder
from llm.client import OpenRouterLLM

llm = OpenRouterLLM()


# =========================
# STEP 1: Load Chapter
# =========================
text = load_chapter(
    class_name="class10",
    subject="science",
    chapter="life_processes"
)


# =========================
# STEP 2: Concept Extraction
# =========================
concept_extractor = ConceptExtractor(llm)
concepts = concept_extractor.extract(text)

print("\n===== CONCEPTS =====\n")
print(json.dumps(concepts, indent=4, ensure_ascii=False))


# =========================
# STEP 3: Relationship Generation (NOW ACTIVE)
# =========================
relationship_generator = RelationshipGenerator(llm)

relationships = relationship_generator.generate(
    hierarchy=concepts,
    chapter_text=text
)

print("\n===== RELATIONSHIPS =====\n")
print(json.dumps(relationships, indent=4, ensure_ascii=False))


# =========================
# STEP 4: Summarization
# =========================
summarizer = Summarizer(llm)
summaries = summarizer.summarize(concepts)

print("\n===== SUMMARIES =====\n")
print(json.dumps(summaries, indent=4, ensure_ascii=False))


# =========================
# STEP 5: Tree Builder
# =========================
tree_builder = TreeBuilder()

final_tree = tree_builder.build(
    hierarchy=concepts,
    summaries=summaries,
    relationships=relationships
)


print("\n===== FINAL MIND MAP =====\n")
print(json.dumps(final_tree, indent=4, ensure_ascii=False))