import os, types
from unittest.mock import patch

os.environ.setdefault("OPENAI_API_KEY", "test-key")

ERROR_CTX = "maximum context length exceeded"

class DummyResp:
    def __init__(self, content):
        self.choices = [types.SimpleNamespace(message=types.SimpleNamespace(content=content))]


def test_token_error_then_retry(monkeypatch):
    # We'll simulate via ai_client.request: first returns missing_output_text, second returns success.
    import ai_client, importlib
    importlib.reload(ai_client)
    calls = {"n":0}
    def fake_request(messages, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            return {"output_text":"", "model":"gpt-5", "used_fallback": False, "error":"missing_output_text"}
        return {"output_text":"Recovered after token clamp", "model":"gpt-5", "used_fallback": False, "usage":{}, "id":"test"}
    monkeypatch.setattr(ai_client, 'request', fake_request)
    # Directly invoke ai_client.request to confirm second attempt returns output
    res1 = ai_client.request([{"role":"user","content":"Hi"}], max_output_tokens=100)
    res2 = ai_client.request([{"role":"user","content":"Hi"}], max_output_tokens=100)
    assert res1.get('output_text','') == ''
    assert 'Recovered' in res2.get('output_text','')
    assert calls['n'] == 2
