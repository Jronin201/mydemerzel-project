import app as flask_app, ai_client
import pytest

app = flask_app.app

CALLS = {}

def fake_request(messages, **kwargs):
    CALLS['called'] = True
    return {
        'output_text': 'Adjusted OK',
        'model': 'gpt-5.2-test',
        'used_fallback': False,
        'id': 'resp_adjust',
        'usage': {'input_tokens': 10, 'output_tokens': 100, 'total_tokens': 110},
        'backoff_ms': 0,
        'breaker_state': 'closed'
    }

def test_preflight_adjust_deterministic(monkeypatch, capsys):
    # Force estimator to return 100000
    monkeypatch.setattr(flash_app:=__import__('app'), 'estimate_input_tokens', lambda parts: 100000)
    monkeypatch.setenv('MODEL_CONTEXT_WINDOW','105000')
    orig_window = ai_client.MODEL_CONTEXT_WINDOW
    ai_client.MODEL_CONTEXT_WINDOW = 105000
    monkeypatch.setenv('OPENAI_MAX_OUTPUT_TOKENS','20000')
    ai_client.OPENAI_MAX_OUTPUT_TOKENS = 20000
    monkeypatch.setattr(ai_client, 'request', fake_request)
    try:
        with app.test_client() as c:
            resp = c.post('/chat', json={'message':'hello','page':'general'})
            assert resp.status_code == 200
            data = resp.get_json()
            assert data['preflight_adjusted'] is True
            assert data['cap_used'] == 5000
            assert CALLS.get('called') is True
    finally:
        ai_client.MODEL_CONTEXT_WINDOW = orig_window
    captured = capsys.readouterr().out
    assert 'preflight_adjust WARN' in captured
    assert 'est_input_tokens=100000' in captured
    assert 'context_window=105000' in captured


def test_preflight_reject_deterministic(monkeypatch, capsys):
    CALLS.clear()
    monkeypatch.setattr(flash_app:=__import__('app'), 'estimate_input_tokens', lambda parts: 950)
    monkeypatch.setenv('MODEL_CONTEXT_WINDOW','1000')
    orig_window = ai_client.MODEL_CONTEXT_WINDOW
    ai_client.MODEL_CONTEXT_WINDOW = 1000
    monkeypatch.setenv('OPENAI_MAX_OUTPUT_TOKENS','20000')
    ai_client.OPENAI_MAX_OUTPUT_TOKENS = 20000
    monkeypatch.setattr(ai_client, 'request', fake_request)
    try:
        with app.test_client() as c:
            resp = c.post('/chat', json={'message':'hello','page':'general'})
            assert resp.status_code == 422
            data = resp.get_json()
            assert 'Context too large' in data['error']
            assert CALLS.get('called') is None  # ensure OpenAI not called
    finally:
        ai_client.MODEL_CONTEXT_WINDOW = orig_window
    captured = capsys.readouterr().out
    # Should not contain adjust WARN for reject
    assert 'preflight_adjust WARN' not in captured
