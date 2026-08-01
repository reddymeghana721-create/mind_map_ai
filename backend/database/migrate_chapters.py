from pathlib import Path

from database.chapter_repository import ChapterRepository

repo = ChapterRepository()

BASE_DIR = Path(__file__).resolve().parent.parent
CHAPTERS_DIR = BASE_DIR / "data" / "chapters"

def migrate():
    print("BASE_DIR:", BASE_DIR)
    print("CHAPTERS_DIR:", CHAPTERS_DIR)
    print("Exists:", CHAPTERS_DIR.exists())

    for file in CHAPTERS_DIR.rglob("*.txt"):
        print(file)

        relative_path = file.relative_to(CHAPTERS_DIR)

        class_name = relative_path.parts[0]
        subject = relative_path.parts[1]
        chapter = file.stem.replace("_", " ").replace("-", " ").title()
        content = file.read_text(encoding="utf-8")

        chapter_data = {
        "class_name": class_name,
        "subject": subject,
        "chapter": chapter,
        "content": content
        }

        result = repo.save_chapter(chapter_data)
        
        print("Inserted:", result)
        print("-" * 40)

        print("Class   :", class_name)
        print("Subject :", subject)
        print("Chapter :", chapter)
        print("Length  :", len(content))
        print("-" * 40)


if __name__ == "__main__":
    migrate()
