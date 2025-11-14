import os

def test_chat_model_fallbacks_configuration(monkeypatch):
    # Provide a fake key so OpenAI client init doesn't fail
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    # Ensure no override via env for model name
    if "OPENAI_CHAT_MODEL" in os.environ:
        monkeypatch.delenv("OPENAI_CHAT_MODEL", raising=False)
    import importlib
    import app
    importlib.reload(app)  # reload to pick up env changes deterministically
    # Primary should default to gpt-5.1
    assert app.OPENAI_CHAT_MODEL == "gpt-5.1", f"Unexpected primary model: {app.OPENAI_CHAT_MODEL}"
    # Fallback list should contain primary then gpt-4o only (mini removed/commented)
    assert app.CHAT_MODEL_FALLBACKS[0] == app.OPENAI_CHAT_MODEL
    assert len(app.CHAT_MODEL_FALLBACKS) == 2, f"Unexpected fallback length: {app.CHAT_MODEL_FALLBACKS}"
    assert app.CHAT_MODEL_FALLBACKS[1] == "gpt-4o", f"Second fallback should be gpt-4o: {app.CHAT_MODEL_FALLBACKS}"
    assert not any("mini" in m for m in app.CHAT_MODEL_FALLBACKS), "mini variant present unexpectedly"
