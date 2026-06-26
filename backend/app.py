from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# ADD ROOT PATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from chapter_loader.loader import load_chapter

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return "Mindmap Backend Running 🚀"


@app.route("/generate", methods=["POST"])
def generate():
    data = request.json

    class_name = data.get("class_name")
    subject = data.get("subject")
    chapter = data.get("chapter")

    print("Request received:", class_name, subject, chapter)

    text = load_chapter(class_name, subject, chapter)

    return jsonify({
        "chapter_text": text
    })


if __name__ == "__main__":
    app.run(debug=True)