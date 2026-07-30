from services.pdf_converter import PDFToTextConverter

converter = PDFToTextConverter(chapters_root="data/chapters")

output_path = converter.convert(
    pdf_path="data/uploads/jesc112.pdf",
    class_name="class10",
    subject="science",
    chapter_name="MagneticEffectsofElectricCurrent"
)

print("Saved to:", output_path)