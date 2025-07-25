#!/usr/bin/env python3
import sys
from pypdf import PdfReader, PdfWriter

if len(sys.argv) != 3:
    print("Usage: python split_dune.py input.pdf pages_per_chunk")
    sys.exit(1)

input_pdf, pages_per = sys.argv[1], int(sys.argv[2])
reader = PdfReader(input_pdf)
total = len(reader.pages)
chunk = PdfWriter()
count = 0
file_index = 1

for i, page in enumerate(reader.pages, start=1):
    chunk.add_page(page)
    if i % pages_per == 0 or i == total:
        out_name = f"documents/dune/sections/dune-manual_{file_index}.pdf"
        with open(out_name, "wb") as out_f:
            chunk.write(out_f)
        print(f"Written {out_name}")
        file_index += 1
        chunk = PdfWriter()