import pymupdf
from pathlib import Path

tests_folder = Path(__file__).parent

font_path = Path(r"C:\Windows\Fonts\arial.ttf")

old_pdf = pymupdf.open()
old_page = old_pdf.new_page()
old_page.insert_text(
    (72, 72),
    "My experience: 2009 - 2013",
    fontfile=str(font_path),
)
old_pdf.save(tests_folder / "test_symbol_old.pdf")
old_pdf.close()

new_pdf = pymupdf.open()
new_page = new_pdf.new_page()
new_page.insert_text(
    (72, 72),
    "My experience: 2009 – 2013",
    fontfile=str(font_path),
)
new_pdf.save(tests_folder / "test_symbol_new.pdf")
new_pdf.close()

print("Symbol test PDFs created successfully.")