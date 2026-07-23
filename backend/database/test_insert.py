from database.chapter_repository import ChapterRepository

repo = ChapterRepository()

chapter = {
    "class_name": "class10",
    "subject": "science",
    "chapter": "life_processes",
    "content": "This is a test chapter stored in MongoDB.",
    "source": "txt"
}

result = repo.save_chapter(chapter)

print(result)