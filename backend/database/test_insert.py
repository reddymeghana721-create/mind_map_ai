from database.chapter_repository import ChapterRepository

repo = ChapterRepository()

chapter = repo.get_chapter(
    "class10",
    "science",
    "life_processes"
)

print(chapter)