import os
import json
from database.mindmap_repository import MindMapRepository
import traceback

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

mindmap_repo = MindMapRepository()

# In-memory cache
_mindmap_cache = {}

# Base folder where generated mindmaps are persisted as JSON
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mindmaps")


def _get_output_path(class_name: str, subject: str, chapter: str) -> str:
    """
    Builds the path: mindmaps/<class_name>/<subject>/<chapter>.json
    """
    folder = os.path.join(OUTPUT_DIR, class_name, subject)
    os.makedirs(folder, exist_ok=True)
    filename = f"{chapter}.json"
    return os.path.join(folder, filename)


def _save_to_disk(class_name: str, subject: str, chapter: str, tree: dict) -> None:
    path = _get_output_path(class_name, subject, chapter)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=2)


def _load_from_disk(class_name: str, subject: str, chapter: str):
    path = _get_output_path(class_name, subject, chapter)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def _list_all_mindmaps():
    """
    Scans OUTPUT_DIR (mindmaps/<class_name>/<subject>/<chapter>.json)
    and returns a list like:
    [
        {"class_name": "class10", "subject": "science", "chapter": "light"},
        ...
    ]
    """
    results = []

    if not os.path.isdir(OUTPUT_DIR):
        return results

    for class_name in sorted(os.listdir(OUTPUT_DIR)):
        class_path = os.path.join(OUTPUT_DIR, class_name)
        if not os.path.isdir(class_path):
            continue

        for subject in sorted(os.listdir(class_path)):
            subject_path = os.path.join(class_path, subject)
            if not os.path.isdir(subject_path):
                continue

            for filename in sorted(os.listdir(subject_path)):
                if filename.endswith(".json"):
                    chapter = filename[:-5]  # strip ".json"
                    results.append({
                        "class_name": class_name,
                        "subject": subject,
                        "chapter": chapter
                    })

    return results


def generate_mindmap(class_name: str, subject: str, chapter: str) -> dict:

    cache_key = f"{class_name}_{subject}_{chapter}"

    # 1. In-memory cache
    if cache_key in _mindmap_cache:
        return _mindmap_cache[cache_key]

    # 2. MongoDB cache
    existing = mindmap_repo.get_mindmap(
    class_name,
    subject,
    chapter
)

    print("Existing mindmap:", existing)

    if existing is not None and "tree" in existing:
     _mindmap_cache[cache_key] = existing["tree"]
     return existing["tree"]

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

    # Save to memory
    _mindmap_cache[cache_key] = final_tree

    # Save to MongoDB
    mindmap_repo.save_mindmap({
    "class_name": class_name,
    "subject": subject,
    "chapter": chapter,
    "tree": final_tree
    })

    # Save JSON (optional backup)
    _save_to_disk(class_name, subject, chapter, final_tree)

    return final_tree
 

@app.route("/api/mindmaps", methods=["GET"])
def list_mindmaps():
    """
    Returns every mindmap already generated and saved on disk,
    so the frontend can render a list/grid of them.
    """
    try:
        mindmaps = _list_all_mindmaps()
        return jsonify({
            "count": len(mindmaps),
            "mindmaps": mindmaps
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


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
        traceback.print_exc()

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