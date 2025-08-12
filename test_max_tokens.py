def test_openai_max_tokens_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MAX_TOKENS", "20000")
    import importlib, app
    importlib.reload(app)
    assert app.OPENAI_MAX_TOKENS == 20000
