from database.mindmap_repository import MindMapRepository

repo = MindMapRepository()

data = {
    "class_name": "class10",
    "subject": "science",
    "chapter": "demo",
    "tree": {
        "label": "Demo MindMap"
    }
}

print(repo.save_mindmap(data))