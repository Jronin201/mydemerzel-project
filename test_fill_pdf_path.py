import json
import os
import subprocess


def test_fill_pdf_accepts_prefixed_template():
    json_path = '/mnt/data/tmp_fields.json'
    pdf_path = '/mnt/data/tmp.pdf'
    with open(json_path, 'w') as f:
        json.dump({'Name': 'Bob'}, f)
    result = subprocess.run(['node', 'fill_pdf.js', 'pdfs/dwarf.pdf', 'tmp'], capture_output=True, text=True)
    assert result.returncode == 0
    assert os.path.exists(pdf_path)
    os.remove(json_path)
    os.remove(pdf_path)
