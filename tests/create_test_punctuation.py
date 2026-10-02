import pymupdf
from pathlib import Path

tests_folder = Path(__file__).parent

old_pdf = pymupdf.open()
old_page = old_pdf.new_page()
old_page.insert_text((72, 72), "This is a guide")
old_pdf.save(tests_folder / "test_punctuation_old.pdf")
old_pdf.close()

new_pdf = pymupdf.open()
new_page = new_pdf.new_page()
new_page.insert_text((72, 72), "This is a guide.")
new_pdf.save(tests_folder / "test_punctuation_new.pdf")
new_pdf.close()

print("Punctuation test PDFs created successfully.")