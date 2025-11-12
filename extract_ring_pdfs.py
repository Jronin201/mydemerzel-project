import os
from pathlib import Path
import fitz  # PyMuPDF


def extract_text_from_pdfs(input_dir: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for pdf_path in input_dir.glob('*.pdf'):
        text_parts = []
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text_parts.append(page.get_text())
        output_file = output_dir / f"{pdf_path.stem}.txt"
        with output_file.open('w', encoding='utf-8') as f:
            f.write("\n".join(text_parts))


if __name__ == "__main__":
    input_directory = Path('documents/the-witcher')
    output_directory = Path('static/text/the-witcher')
    extract_text_from_pdfs(input_directory, output_directory)
