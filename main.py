from chapter_loader.loader import load_chapter
from concept_extractor.extractor import ConceptExtractor
from relationship_generator.generator import RelationshipGenerator
from summarizer.summarizer import Summarizer
from tree_builder.builder import TreeBuilder
from llm.client import OpenRouterLLM

llm = OpenRouterLLM()


# STEP 1: Load chapter
text = load_chapter(
    class_name="class10",
    subject="science",
    chapter="life_processes"
)

print("\n===== CHAPTER TEXT =====\n")
print(text)


# STEP 2: Concept Extraction
concept_extractor = ConceptExtractor(llm)
concepts = concept_extractor.extract(text)

print("\n===== CONCEPTS =====\n")
print(concepts)


# STEP 3: Relationship Generation
relationship_generator = RelationshipGenerator(llm)
relationships = relationship_generator.generate(concepts["concepts"])

print("\n===== RELATIONSHIPS =====\n")
print(relationships)


# STEP 4: Summarization
summarizer = Summarizer()
summaries = summarizer.summarize(concepts)

print("\n===== SUMMARIES =====\n")
print(summaries)


# STEP 5: Tree Builder (Final Mind Map)
tree_builder = TreeBuilder()

final_tree = tree_builder.build(
    concepts=concepts["concepts"],
    relationships=relationships,   # ✅ FIXED HERE
    summaries=summaries["nodes"]
)

print("\n===== FINAL MIND MAP =====\n")
print(final_tree)