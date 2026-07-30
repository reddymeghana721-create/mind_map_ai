from database.connection import db


class MindMapRepository:

    def __init__(self):
        self.collection = db["mindmaps"] if db is not None else None

    def save_mindmap(self, data):
        if self.collection is None:
            return None
        try:
            result = self.collection.insert_one(data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error saving to MongoDB: {e}")
            return None

    def get_mindmap(self, class_name, subject, chapter):
        if self.collection is None:
            return None
        try:
            return self.collection.find_one({
                "class_name": class_name,
                "subject": subject,
                "chapter": chapter
            })
        except Exception as e:
            print(f"Error reading from MongoDB: {e}")
            return None

    def get_all_mindmaps(self):
        if self.collection is None:
            return []
        try:
            return list(
                self.collection.find({}, {"tree": 0})
            )
        except Exception as e:
            print(f"Error listing from MongoDB: {e}")
            return []