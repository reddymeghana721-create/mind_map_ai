from pdf_converter import PDFToTextConverter

converter = PDFToTextConverter(chapters_root="chapters")

output_path = converter.convert(
    pdf_path="uploads/jemh104.pdf",
    class_name="class10",
    subject="maths",
    chapter_name="QUADRATIC EQUATIONS"
)

print("Saved to:", output_path)