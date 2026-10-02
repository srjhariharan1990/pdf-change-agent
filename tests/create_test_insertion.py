import pymupdf
from pathlib import Path

tests_folder = Path(__file__).parent

old_pdf = pymupdf.open()
old_page = old_pdf.new_page()
old_page.insert_text((72, 72), "I am a technical writer.")
old_pdf.save(tests_folder / "test_insertion_old.pdf")
old_pdf.close()

new_pdf = pymupdf.open()
new_page = new_pdf.new_page()
new_page.insert_text((72, 72), "I am a senior technical writer at Oracle.")
new_pdf.save(tests_folder / "test_insertion_new.pdf")
new_pdf.close()

print("Insertion test PDFs created successfully.")