import os
import types
from unittest.mock import patch, MagicMock

os.environ.setdefault("OPENAI_API_KEY", "test-key")

class FakeModelUnavailable(Exception):
    pass

# Simulate classification as model unavailable by including key phrase
ERROR_TEXT = "The model is unavailable right now"


def fake_unavailable_call(*args, **kwargs):
    raise Exception(ERROR_TEXT)


def fake_success_call(*args, **kwargs):
    # Minimal structure resembling OpenAI response
    return types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content="Fallback OK"))])


def test_primary_unavailable_triggers_fallback(monkeypatch):
    # Ensure default model
    monkeypatch.setenv("OPENAI_CHAT_MODEL", "gpt-5.0")
    import importlib, app
    importlib.reload(app)

    # Patch first call (primary) to raise, fallback model call to succeed
    call_sequence = []

    def conditional_call(model=None, **kwargs):
        call_sequence.append(model)
        if model == "gpt-5.0":
            raise Exception(ERROR_TEXT)
        return fake_success_call()

    with patch.object(app.client.chat.completions, 'create', side_effect=conditional_call):
        with app.app.test_client() as c:
            resp = c.post('/chat', json={"message": "Explain combat", "page": "pendragon"})
            data = resp.get_json()
            assert resp.status_code == 200
            assert "Fallback OK" in data.get("response", "")
            assert data.get("fallback_used") is True
            assert any(m == "gpt-5.0" for m in call_sequence)
            assert any(m == "gpt-4o" for m in call_sequence)
