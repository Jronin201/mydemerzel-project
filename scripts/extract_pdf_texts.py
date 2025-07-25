from pathlib import Path
import fitz  # PyMuPDF

input_dir = Path("documents/the-one-ring")

for pdf_file in input_dir.glob("*.pdf"):
    output_file = input_dir / (pdf_file.stem + ".txt")
    with fitz.open(pdf_file) as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    output_file.write_text(text, encoding="utf-8")
    print(f"Extracted text from: {pdf_file.name}")
