from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

def load_chapter(class_name, subject, chapter):
    file_path = (
        BASE_DIR
        / "chapters"
        / class_name
        / subject
        / f"{chapter}.txt"
    )

    if not file_path.exists():
        raise FileNotFoundError(
            f"Chapter not found: {file_path}"
        )

    return file_path.read_text(
        encoding="utf-8"
    )