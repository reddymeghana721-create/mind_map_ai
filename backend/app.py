from flask import Flask, jsonify
from flask_cors import CORS

from chapter_loader.loader import load_chapter
from concept_extractor.extractor import ConceptExtractor
from relationship_generator.generator import RelationshipGenerator
from summarizer.summarizer import Summarizer
from tree_builder.builder import TreeBuilder
from llm.client import OpenRouterLLM
from validator.validator import Validator   # NEW

app = Flask(__name__)
CORS(app)

llm = OpenRouterLLM()

concept_extractor = ConceptExtractor(llm)
relationship_generator = RelationshipGenerator(llm)
summarizer = Summarizer(llm)
tree_builder = TreeBuilder()
validator = Validator()   # NEW

# In-memory cache
_mindmap_cache = {}


def generate_mindmap(class_name: str, subject: str, chapter: str) -> dict:

    cache_key = f"{class_name}_{subject}_{chapter}"

    if cache_key in _mindmap_cache:
        return _mindmap_cache[cache_key]

    # ------------------------------------
    # Load Chapter
    # ------------------------------------
    text = load_chapter(
        class_name=class_name,
        subject=subject,
        chapter=chapter
    )

    # ------------------------------------
    # Concept Extraction
    # ------------------------------------
    concepts = concept_extractor.extract(text)

    # ------------------------------------
    # Relationship Generation
    # ------------------------------------
    relationships = relationship_generator.generate(
        hierarchy=concepts,
        chapter_text=text
    )

    # ------------------------------------
    # Summaries
    # ------------------------------------
    summaries = summarizer.summarize(concepts)

    # ------------------------------------
    # VALIDATION (NEW)
    # ------------------------------------
    concepts, relationships, summaries = validator.validate(
        concepts,
        relationships,
        summaries
    )

    # ------------------------------------
    # Build Final Tree
    # ------------------------------------
    final_tree = tree_builder.build(
        hierarchy=concepts,
        summaries=summaries,
        relationships=relationships
    )

    _mindmap_cache[cache_key] = final_tree

    return final_tree


@app.route("/api/mindmap/<class_name>/<subject>/<chapter>", methods=["GET"])
def get_mindmap(class_name, subject, chapter):

    try:
        tree = generate_mindmap(
            class_name,
            subject,
            chapter
        )

        return jsonify(tree)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


@app.route("/api/mindmap/<chapter>", methods=["GET"])
def get_mindmap_default(chapter):

    try:
        tree = generate_mindmap(
            "class10",
            "science",
            chapter
        )

        return jsonify(tree)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok"
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )