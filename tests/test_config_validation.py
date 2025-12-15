import importlib, os, sys, importlib.util, types
import pytest

TARGET_MODULE = 'app'

INVALID_CASES = [
    ({'OPENAI_MODEL':''}, 'OPENAI_MODEL missing or empty'),
    ({'OPENAI_REASONING_EFFORT':'ultra'}, 'OPENAI_REASONING_EFFORT'),
    ({'OPENAI_MAX_OUTPUT_TOKENS':'notint'}, 'OPENAI_MAX_OUTPUT_TOKENS'),
    ({'OPENAI_MAX_OUTPUT_TOKENS':'10'}, 'OPENAI_MAX_OUTPUT_TOKENS must be >= 64'),
    ({'OPENAI_TOOL_CHOICE':'magic'}, 'OPENAI_TOOL_CHOICE'),
    ({'AI_BACKOFF_BASE_MS':'0'}, 'AI_BACKOFF_BASE_MS'),
    ({'AI_BACKOFF_CAP_MS':'-5'}, 'AI_BACKOFF_CAP_MS'),
]

@pytest.mark.parametrize('env_overrides,needle', INVALID_CASES)
def test_startup_config_invalid(monkeypatch, env_overrides, needle, capsys):
    # Clear module if already imported
    if TARGET_MODULE in sys.modules:
        del sys.modules[TARGET_MODULE]
    # Set overrides
    for k,v in env_overrides.items():
        monkeypatch.setenv(k, v)
    # Ensure baseline envs present
    monkeypatch.setenv('OPENAI_MODEL', env_overrides.get('OPENAI_MODEL','gpt-5.2'))
    # Force reload
    with pytest.raises(SystemExit):
        import app  # noqa: F401
    out = capsys.readouterr().out
    assert needle in out


def test_startup_config_valid(monkeypatch, capsys):
    if TARGET_MODULE in sys.modules:
        del sys.modules[TARGET_MODULE]
    # Provide valid defaults
    monkeypatch.setenv('OPENAI_MODEL','gpt-5.2')
    monkeypatch.delenv('OPENAI_REASONING_EFFORT', raising=False)  # falls back to low
    monkeypatch.delenv('OPENAI_MAX_OUTPUT_TOKENS', raising=False)
    monkeypatch.delenv('OPENAI_TOOL_CHOICE', raising=False)
    monkeypatch.delenv('AI_BACKOFF_BASE_MS', raising=False)
    monkeypatch.delenv('AI_BACKOFF_CAP_MS', raising=False)
    import app  # noqa: F401
    out = capsys.readouterr().out
    config_lines = [ln for ln in out.splitlines() if ln.startswith('[CONFIG]')]
    assert len(config_lines) == 1
