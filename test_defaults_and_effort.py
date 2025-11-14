import ai_client
import app as flask_app

app = flask_app.app


def test_defaults_medium_effort_and_20k(monkeypatch):
    # Ensure env not overriding
    monkeypatch.delenv('OPENAI_REASONING_EFFORT', raising=False)
    monkeypatch.delenv('OPENAI_MAX_OUTPUT_TOKENS', raising=False)
    captured = {}
    def fake_request(messages, **kwargs):
        captured['kwargs'] = kwargs
        return {
            'output_text': 'Short',
            'model': 'gpt-5.1-defaults',
            'used_fallback': False,
            'id': 'resp_defaults',
            'usage': {'input_tokens': 10, 'output_tokens': 2, 'total_tokens': 12},
            'backoff_ms': 0,
            'breaker_state': 'closed'
        }
    monkeypatch.setattr(ai_client, 'request', fake_request)
    with app.test_client() as c:
        resp = c.post('/chat', json={'message':'Ping','page':'general'})
        assert resp.status_code == 200
    # ai_client stores last kwargs in global when building input; we rely on captured
    eff = captured['kwargs']['reasoning']['effort'] if 'kwargs' in captured else None
    max_out = captured['kwargs']['max_output_tokens'] if 'kwargs' in captured else None
    assert eff == 'medium'
    assert max_out == 20000


def test_high_effort_override(monkeypatch):
    captured = {}
    def fake_request(messages, **kwargs):
        captured['kwargs'] = kwargs
        return {
            'output_text': 'High effort reply',
            'model': 'gpt-5.1-high',
            'used_fallback': False,
            'id': 'resp_high',
            'usage': {'input_tokens': 15, 'output_tokens': 5, 'total_tokens': 20},
            'backoff_ms': 0,
            'breaker_state': 'closed'
        }
    monkeypatch.setattr(ai_client, 'request', fake_request)
    with app.test_client() as c:
        resp = c.post('/chat', json={'message':'Do complex reasoning','page':'general','high_effort':True})
        assert resp.status_code == 200
    eff = captured['kwargs']['reasoning']['effort'] if 'kwargs' in captured else None
    assert eff == 'high'
