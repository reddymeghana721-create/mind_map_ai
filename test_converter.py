from pdf_converter import PDFToTextConverter

converter = PDFToTextConverter(chapters_root="chapters")

output_path = converter.convert(
    pdf_path="uploads/jesc105.pdf",
    class_name="class10",
    subject="science",
    chapter_name="life_processes"
)

print("Saved to:", output_path)