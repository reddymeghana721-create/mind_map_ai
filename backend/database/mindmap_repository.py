from database.connection import db

# Collection
mindmaps = db["mindmaps"] if db is not None else None


class MindMapRepository:

    def save_mindmap(self, data):
        if mindmaps is None:
            return None
        result = mindmaps.insert_one(data)
        return str(result.inserted_id)

    def get_mindmap(self, class_name, subject, chapter):
        if mindmaps is None:
            return None
        return mindmaps.find_one({
            "class_name": class_name,
            "subject": subject,
            "chapter": chapter
        })

    def get_all_mindmaps(self):
        if mindmaps is None:
            return []
        return list(
            mindmaps.find({}, {"tree": 0})
        )