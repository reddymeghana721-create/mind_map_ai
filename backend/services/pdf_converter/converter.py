import os
import sys
import fitz
from .cleaner import TextCleaner


class PDFToTextConverter:

    def __init__(self, chapters_root="data/chapters", repeated_headers=None):
        self.chapters_root = chapters_root
        self.cleaner = TextCleaner(repeated_headers=repeated_headers)

    def convert(self, pdf_path, class_name, subject, chapter_name=None):
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        if chapter_name is None:
            chapter_name = os.path.splitext(os.path.basename(pdf_path))[0]

        raw_text = self._extract_text(pdf_path)
        text = self.cleaner.clean(raw_text)

        if not text.strip():
            raise ValueError(
                f"No text could be extracted from {pdf_path}. "
                "This PDF may be a scanned/image-only document with no text layer."
            )

        output_dir = os.path.join(self.chapters_root, class_name, subject)
        os.makedirs(output_dir, exist_ok=True)

        chapter_name = chapter_name.strip()
        output_path = os.path.join(output_dir, f"{chapter_name}.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

        return output_path

    def _extract_text(self, pdf_path):
        fitz.TOOLS.mupdf_display_errors(False)

        doc = fitz.open(pdf_path)
        pages = []

        for page_num, page in enumerate(doc):
            try:
                page_text = page.get_text().strip()
            except Exception as e:
                print(f"⚠️  Failed to extract page {page_num + 1}: {e}", file=sys.stderr)
                page_text = ""
            pages.append(page_text)

        doc.close()
        return "\n\n".join(pages)
