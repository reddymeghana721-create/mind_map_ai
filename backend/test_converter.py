from pdf_converter import PDFToTextConverter

converter = PDFToTextConverter(chapters_root="chapters")

output_path = converter.convert(
    pdf_path="data/uploads/jesc102.pdf",
    class_name="class10",
    subject="science",
    chapter_name="Acids, Bases and Salts"
)

print("Saved to:", output_path)