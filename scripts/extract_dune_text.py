import fitz
from pathlib import Path

# Directory containing the split PDFs
pdf_dir = Path("documents/dune/sections")
output_file = Path("documents/dune/dune.txt")

with output_file.open("w", encoding="utf-8") as out:
    for pdf_path in sorted(pdf_dir.glob("*.pdf")):
        doc = fitz.open(pdf_path)
        for page in doc:
            text = page.get_text()
            out.write(text + "\n")
        out.write("\n\n--- End of {}\n\n".format(pdf_path.name))
