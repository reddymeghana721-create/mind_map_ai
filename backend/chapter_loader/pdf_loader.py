import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_path):
    """
    Extract all text from a PDF file.
    """
    doc = fitz.open(pdf_path)

    text = ""

    for page in doc:
        text += page.get_text()

    doc.close()

    return text