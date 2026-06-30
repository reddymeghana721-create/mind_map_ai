from flask import Flask, request, jsonify
from flask_cors import CORS

from chapter_loader.loader import load_chapter
from services.llm_client import OpenRouterLLM
from services.concept_extractor import ConceptExtractor
from services.relationship_generator import RelationshipGenerator
from services.summarizer import Summarizer
from services.tree_builder import TreeBuilder

app = Flask(__name__)
CORS(app)

llm = OpenRouterLLM()

@app.route("/")
def home():
    return "Mindmap Backend Running 🚀"


@app.route("/generate", methods=["POST"])
def generate():
    data = request.json

    class_name = data.get("class_name")
    subject = data.get("subject")
    chapter = data.get("chapter")

    # 1. Load chapter
    text = load_chapter(class_name, subject, chapter)

    # 2. Extract concepts
    concept_extractor = ConceptExtractor(llm)
    concepts = concept_extractor.extract(text)

    # 3. Relationships
    relationship_generator = RelationshipGenerator(llm)
    relationships = relationship_generator.generate(concepts["concepts"])

    # 4. Summaries
    summarizer = Summarizer()
    summaries = summarizer.summarize(concepts)

    # 5. Final tree
    tree_builder = TreeBuilder()
    final_tree = tree_builder.build(
        concepts=concepts["concepts"],
        relationships=relationships["relationships"],
        summaries=summaries["nodes"]
    )

    return jsonify(final_tree)


if __name__ == "__main__":
    app.run(debug=True)