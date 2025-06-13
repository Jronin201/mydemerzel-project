import json
from app import app


def test_chat_invalid_json():
    with app.test_client() as client:
        response = client.post('/chat', data='bad json', content_type='application/json')
        assert response.status_code == 400
        assert response.get_json() == {'error': 'Invalid JSON payload'}


