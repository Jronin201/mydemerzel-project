from pathlib import Path
import fitz  # PyMuPDF

input_dir = Path("documents/the-witcher")
output_dir = Path("static/text/the-witcher")
output_dir.mkdir(parents=True, exist_ok=True)

for pdf_file in input_dir.glob("*.pdf"):
    output_file = output_dir / (pdf_file.stem + ".txt")
    with fitz.open(pdf_file) as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    output_file.write_text(text, encoding="utf-8")
    print(f"Extracted text from: {pdf_file.name}")
