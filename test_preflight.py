import app as flask_app, ai_client
import pytest

app = flask_app.app


def test_preflight_adjust(monkeypatch):
    # Use a large user message to push over window threshold for default 20000 output
    # We'll pick a reduced window that is still larger than input so adjustment not rejection.
    # Build user input ~15000 chars (~3750 tokens). Window 12000 forces adjust (allowed < 20000 but > 64) but must be > est_input. So compute sizes.
    big_user = 'u'*8000  # ~2000 tokens est
    monkeypatch.setenv('MODEL_CONTEXT_WINDOW','10000')
    ai_client.MODEL_CONTEXT_WINDOW = 10000
    with app.test_client() as c:
        resp = c.post('/chat', json={'message': big_user, 'page':'general'})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['preflight_adjusted'] is True
        assert data['cap_used'] < ai_client.OPENAI_MAX_OUTPUT_TOKENS
        assert data['cap_used'] >= 64
        assert data['est_input_tokens'] + data['cap_used'] <= data['context_window']


def test_preflight_reject(monkeypatch):
    # Very small window to force reject (input itself too large)
    monkeypatch.setenv('MODEL_CONTEXT_WINDOW','100')
    ai_client.MODEL_CONTEXT_WINDOW = 100
    big_user = 'y' * 1000  # ~250 tokens -> exceeds
    with app.test_client() as c:
        resp = c.post('/chat', json={'message': big_user, 'page':'general'})
        assert resp.status_code == 422
        data = resp.get_json()
        assert 'Context too large' in data['error']
