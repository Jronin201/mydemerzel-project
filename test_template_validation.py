import json
from unittest.mock import patch, MagicMock
from app import app, ALLOWED_TEMPLATES


def _post_save(client, template):
    payload = {
        "name": "Test",
        "template": template,
        "fieldData": {"a": 1}
    }
    return client.post('/save-character', data=json.dumps(payload), content_type='application/json')


def test_save_character_valid_template():
    with app.test_client() as client:
        with patch('subprocess.run') as run_mock:
            run_mock.return_value = MagicMock(returncode=0, stdout='', stderr='')
            resp = _post_save(client, next(iter(ALLOWED_TEMPLATES)))
            assert resp.status_code == 200


def test_save_character_template_not_allowed():
    with app.test_client() as client:
        resp = _post_save(client, 'pdfs/invalid.pdf')
        assert resp.status_code == 400
        assert resp.get_json()['error'] == 'Template not allowed'


def test_save_character_template_traversal():
    with app.test_client() as client:
        resp = _post_save(client, '../secret.pdf')
        assert resp.status_code == 400
        assert resp.get_json()['error'] == 'Invalid template path'
