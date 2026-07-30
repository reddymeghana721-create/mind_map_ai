from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def load_chapter(class_name: str, subject: str, chapter: str) -> str:
    # Primary: data/chapters
    primary_path = (
        BASE_DIR
        / "data"
        / "chapters"
        / class_name
        / subject
        / f"{chapter}.txt"
    )

    if primary_path.exists():
        return primary_path.read_text(encoding="utf-8")

    # Fallback: chapters
    fallback_path = (
        BASE_DIR
        / "chapters"
        / class_name
        / subject
        / f"{chapter}.txt"
    )

    if fallback_path.exists():
        return fallback_path.read_text(encoding="utf-8")

    raise FileNotFoundError(
        f"Chapter file not found in {primary_path} or {fallback_path}"
    )
