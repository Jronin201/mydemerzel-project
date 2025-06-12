import json
import os
from unittest.mock import patch, MagicMock

from app import app, normalize_filename, ALLOWED_TEMPLATES


def _create_dummy_pdf(path):
    with open(path, 'wb') as f:
        f.write(b"%PDF-1.4 dummy")


def test_save_and_load_character():
    name = "Test Character"
    template = next(iter(ALLOWED_TEMPLATES))
    field_data = {"Name": "Bob"}
    payload = {"name": name, "template": template, "fieldData": field_data}
    normalized = normalize_filename(name)
    pdf_path = f"/mnt/data/{normalized}.pdf"
    json_path = f"/mnt/data/{normalized}_fields.json"

    # clean up before
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    if os.path.exists(json_path):
        os.remove(json_path)

    def dummy_run(args, capture_output=True, text=True):
        _create_dummy_pdf(pdf_path)
        return MagicMock(returncode=0, stdout="", stderr="")

    with app.test_client() as client:
        with patch('subprocess.run', side_effect=dummy_run):
            resp = client.post('/save-character', data=json.dumps(payload), content_type='application/json')
            assert resp.status_code == 200
            assert os.path.exists(pdf_path)

            load_resp = client.get(f'/load-character/{name}')
            assert load_resp.status_code == 200
            assert load_resp.headers['Content-Type'] == 'application/pdf'
            assert load_resp.data.startswith(b'%PDF')

    # clean up after
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    if os.path.exists(json_path):
        os.remove(json_path)
