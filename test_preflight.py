import app as flask_app, ai_client
import pytest

app = flask_app.app


def test_preflight_reject(monkeypatch):
    # Very small window to force reject (input itself too large)
    monkeypatch.setenv('MODEL_CONTEXT_WINDOW','100')
    orig_window = ai_client.MODEL_CONTEXT_WINDOW
    ai_client.MODEL_CONTEXT_WINDOW = 100
    big_user = 'y' * 1000  # ~250 tokens -> exceeds
    try:
        with app.test_client() as c:
            resp = c.post('/chat', json={'message': big_user, 'page':'general'})
            assert resp.status_code == 422
            data = resp.get_json()
            assert 'Context too large' in data['error']
    finally:
        # Restore global to avoid leaking into other tests (SSE contract etc.)
        ai_client.MODEL_CONTEXT_WINDOW = orig_window
