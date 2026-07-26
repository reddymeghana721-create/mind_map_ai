from database.connection import db

# Collection
mindmaps = db["mindmaps"]


class MindMapRepository:

    def save_mindmap(self, data):
        result = mindmaps.insert_one(data)
        return str(result.inserted_id)

    def get_mindmap(self, class_name, subject, chapter):
        return mindmaps.find_one({
            "class_name": class_name,
            "subject": subject,
            "chapter": chapter
        })

    def get_all_mindmaps(self):
        return list(
            mindmaps.find({}, {"tree": 0})
        )