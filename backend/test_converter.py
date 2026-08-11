from pdf_converter import PDFToTextConverter

converter = PDFToTextConverter(chapters_root="chapters")

output_path = converter.convert(
<<<<<<< Updated upstream
    pdf_path="uploads/jesc112.pdf",
    class_name="class10",
    subject="science",
    chapter_name="Magnetic Effects of Electric Current"
=======
    pdf_path="data/uploads/jesc102.pdf",
    class_name="class10",
    subject="science",
    chapter_name="Acids, Bases and Salts"
>>>>>>> Stashed changes
)

print("Saved to:", output_path)