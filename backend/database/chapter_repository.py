from database.connection import db

# Collection
chapters = db["chapters"]


class ChapterRepository:

    def save_chapter(self, chapter_data):
        """Insert chapter only if it doesn't already exist"""

        existing = chapters.find_one({
            "class_name": chapter_data["class_name"],
            "subject": chapter_data["subject"],
            "chapter": chapter_data["chapter"]
        })

        if existing:
            return "Chapter already exists"

        result = chapters.insert_one(chapter_data)
        return str(result.inserted_id)

    def get_chapter(self, class_name, subject, chapter):
        """Fetch chapter by class, subject and chapter name"""

        return chapters.find_one({
            "class_name": class_name,
            "subject": subject,
            "chapter": chapter
        })

    def get_all_chapters(self):
        """Fetch all chapters"""

        return list(chapters.find({}, {"content": 0}))