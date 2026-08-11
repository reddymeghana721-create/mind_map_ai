import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.chapter_loader.loader import load_chapter
from services.concept_extractor.extractor import ConceptExtractor

text = load_chapter('class10', 'science', 'MagneticEffectsofElectricCurrent')

class MockLLM:
    def generate(self, prompt):
        import re
        m = re.search(r'Section Topic: "([^"]+)"', prompt)
        sec = m.group(1) if m else "Section"
        return json.dumps({
            "name": sec,
            "subtopics": [
                {"name": "Core Concepts", "subtopics": [{"name": "Definition and Discovery", "subtopics": []}, {"name": "Key Mechanism", "subtopics": []}]},
                {"name": "Properties and Rules", "subtopics": [{"name": "Direction of Field", "subtopics": []}, {"name": "Magnitude Factors", "subtopics": []}]}
            ]
        })

extractor = ConceptExtractor(MockLLM())
result = extractor.extract(text)

print("Extracted Topics Count:", len(result["topics"]))
for t in result["topics"]:
    print("Topic:", t["name"])
    for sub in t.get("subtopics", []):
        print("  - Subtopic:", sub["name"])
