from flask import Flask, jsonify
from flask_cors import CORS

from chapter_loader.loader import load_chapter
from concept_extractor.extractor import ConceptExtractor
from relationship_generator.generator import RelationshipGenerator
from summarizer.summarizer import Summarizer
from tree_builder.builder import TreeBuilder
from llm.client import OpenRouterLLM

app = Flask(__name__)
CORS(app)  # allow the Vite dev server (localhost:5173) to call this API

llm = OpenRouterLLM()
concept_extractor = ConceptExtractor(llm)
relationship_generator = RelationshipGenerator(llm)
summarizer = Summarizer(llm)
tree_builder = TreeBuilder()

# In-memory cache so repeat requests for the same chapter don't re-run
# every LLM call. Key: "class_subject_chapter" -> final_tree dict.
_mindmap_cache = {}


def generate_mindmap(class_name: str, subject: str, chapter: str) -> dict:
    cache_key = f"{class_name}_{subject}_{chapter}"
    if cache_key in _mindmap_cache:
        return _mindmap_cache[cache_key]

    text = load_chapter(class_name=class_name, subject=subject, chapter=chapter)

    concepts = concept_extractor.extract(text)
    relationships = relationship_generator.generate(hierarchy=concepts, chapter_text=text)
    summaries = summarizer.summarize(concepts)

    final_tree = tree_builder.build(
        hierarchy=concepts,
        summaries=summaries,
        relationships=relationships,
    )

    _mindmap_cache[cache_key] = final_tree
    return final_tree


@app.route("/api/mindmap/<class_name>/<subject>/<chapter>", methods=["GET"])
def get_mindmap(class_name, subject, chapter):
    try:
        tree = generate_mindmap(class_name, subject, chapter)
        return jsonify(tree)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Shortcut matching your original main.py hardcoded call:
# GET /api/mindmap/life_processes -> class10/science/life_processes
@app.route("/api/mindmap/<chapter>", methods=["GET"])
def get_mindmap_default(chapter):
    try:
        tree = generate_mindmap("class10", "science", chapter)
        return jsonify(tree)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)