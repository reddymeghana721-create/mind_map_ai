from pathlib import Path


def load_chapter(class_name, subject, chapter):
    file_path = (
        Path("chapters")
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