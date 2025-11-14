import json
import re
import ai_client
import app as flask_app
import pytest

app = flask_app.app

def count_paragraphs(text):
    return len([p for p in text.split('\n') if p.strip()])

def test_short_scene_default(monkeypatch):
    monkeypatch.setenv('OPENAI_STREAM_RESPONSES','false')
    # Simulate a short scene (2 paragraphs, no [END SCENE])
    short_scene = "Para one.\n\nPara two."
    def fake_request(messages, **kwargs):
        return {
            'output_text': short_scene,
            'model': 'gpt-5.1-short-test',
            'used_fallback': False,
            'id': 'resp_short_scene',
            'usage': {'input_tokens': 100, 'output_tokens': 120, 'total_tokens': 220},
            'backoff_ms': 0,
            'breaker_state': 'closed'
        }
    monkeypatch.setattr(ai_client, 'request', fake_request)
    with app.test_client() as c:
        resp = c.post('/chat', json={'message':'Give me a scene','page':'general'})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['fallback'] is False
        assert count_paragraphs(data['message']) <= 2
        assert '[END SCENE]' not in data['message']

def test_extended_scene_override(monkeypatch):
    monkeypatch.setenv('OPENAI_STREAM_RESPONSES','false')
    # Simulate extended scene (>2 paragraphs, ends with [END SCENE])
    extended_scene = "Para one.\n\nPara two.\n\nPara three.\n\nPara four. [END SCENE]"
    def fake_request(messages, **kwargs):
        return {
            'output_text': extended_scene,
            'model': 'gpt-5.1-extended-test',
            'used_fallback': False,
            'id': 'resp_extended_scene',
            'usage': {'input_tokens': 100, 'output_tokens': 220, 'total_tokens': 320},
            'backoff_ms': 0,
            'breaker_state': 'closed'
        }
    monkeypatch.setattr(ai_client, 'request', fake_request)
    with app.test_client() as c:
        resp = c.post('/chat', json={'message':'Give me a longer scene','page':'general','scene_style':'extended'})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['fallback'] is False
        assert count_paragraphs(data['message']) > 2
        assert '[END SCENE]' not in data['message']
        # Should end cleanly (marker stripped)
        assert not data['message'].strip().endswith('[END SCENE]')
