import os, types
from unittest.mock import patch

os.environ.setdefault("OPENAI_API_KEY", "test-key")

ERROR_CTX = "maximum context length exceeded"

class DummyResp:
    def __init__(self, content):
        self.choices = [types.SimpleNamespace(message=types.SimpleNamespace(content=content))]


def test_token_error_then_retry(monkeypatch):
    monkeypatch.setenv("OPENAI_CHAT_MODEL", "gpt-5.0")
    import importlib, app
    importlib.reload(app)

    attempts = {"count": 0}

    def side_effect(model=None, **kwargs):
        attempts["count"] += 1
        # First attempt for primary triggers token error
        if attempts["count"] == 1:
            raise Exception(ERROR_CTX)
        return DummyResp("Recovered after token clamp")

    with patch.object(app.client.chat.completions, 'create', side_effect=side_effect):
        content, used = app.chat_completion_with_fallback([
            {"role": "system", "content": "Test"},
            {"role": "user", "content": "Hi"}
        ], app.CHAT_MODEL_FALLBACKS, max_tokens=20000)
        assert "Recovered" in content
        assert used == "gpt-5.0"
        assert attempts["count"] == 2  # one retry
