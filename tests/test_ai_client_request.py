import os, sys, types
import pytest

# Ensure project root on path for direct module import
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import ai_client

class DummyUsage:
    def __init__(self, input_tokens=10, output_tokens=20):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.total_tokens = input_tokens + output_tokens

class DummyResp:
    def __init__(self, output_text=None, model="gpt-5.1-2025-08-07", rid="resp_test_1", usage=None):
        self.output_text = output_text
        self.model = model
        self.id = rid
        self.usage = usage or DummyUsage()

class DummyClient:
    def __init__(self, sequence):
        self.sequence = list(sequence)
        self.calls = []
        class RespNamespace:
            def __init__(self, outer):
                self.outer = outer
            def create(self, **kwargs):
                outer = self.outer
                outer.calls.append(kwargs)
                if not outer.sequence:
                    raise RuntimeError("No more scripted responses")
                item = outer.sequence.pop(0)
                if isinstance(item, Exception):
                    raise item
                return item
        self.responses = RespNamespace(self)

@pytest.fixture(autouse=True)
def patch_client(monkeypatch):
    # Ensure consistent config
    monkeypatch.setenv("OPENAI_MODEL", "gpt-5.1")
    monkeypatch.setenv("OPENAI_MAX_OUTPUT_TOKENS", "256")
    # Replace internal _client after module import
    yield
    # cleanup none

def test_returns_plain_text(monkeypatch):
    dummy = DummyClient([DummyResp(output_text="Hello world")])
    monkeypatch.setattr(ai_client, "_client", dummy)
    res = ai_client.request([{"role":"user","content":"Hi"}])
    assert res["output_text"] == "Hello world"
    assert res["usage"]["output_tokens"] == 20
    assert dummy.calls[0]["model"] == "gpt-5.1"

def test_log_observability_and_fallback(monkeypatch, capsys):
    # Hard failure then success fallback
    class HardErr(Exception):
        status_code = 500
    dummy = DummyClient([HardErr("boom"), DummyResp(output_text="OK", model="gpt-4o-2025-08-07", rid="resp_fallback")])
    monkeypatch.setattr(ai_client, "_client", dummy)
    res = ai_client.request([{"role":"user","content":"Ping"}])
    assert res["used_fallback"] is True
    captured = capsys.readouterr().out
    log_text = captured
    assert "openai.model=gpt-5.1" in log_text
    assert "fallback_trigger" in log_text
    assert "openai.model=gpt-4o" in log_text or "gpt-4o-2025" in log_text
    assert "openai.resp_id=resp_fallback" in log_text
    assert "openai.usage.output_tokens" in log_text

def test_config_enforcement(monkeypatch):
    # Force invalid low max_output_tokens and ensure override to >=64
    monkeypatch.setenv("OPENAI_MAX_OUTPUT_TOKENS", "10")
    # Re-import config (simulate reload minimal)
    import importlib
    importlib.reload(ai_client)
    dummy = DummyClient([DummyResp(output_text="Hi")])
    monkeypatch.setattr(ai_client, "_client", dummy)
    res = ai_client.request([{"role":"user","content":"Test"}], max_output_tokens=5)
    assert res["output_text"] == "Hi"
    outgoing = ai_client._last_ai_kwargs
    assert outgoing["max_output_tokens"] >= 64
    # Disallowed fields (temperature) not present
    assert "temperature" not in outgoing
    # tool_choice default none
    assert outgoing["tool_choice"] == "none"

def test_reasoning_only_retry_assertions(monkeypatch):
    # First missing output; second provides
    dummy = DummyClient([DummyResp(output_text=None), DummyResp(output_text="Done")])
    monkeypatch.setattr(ai_client, "_client", dummy)
    res = ai_client.request([{"role":"user","content":"Explain"}], max_output_tokens=100)
    assert res["output_text"] == "Done"
    # Second call has increased tokens & low effort
    first, second = dummy.calls
    assert second["reasoning"]["effort"] == "low"
    assert second["max_output_tokens"] >= first["max_output_tokens"]

def test_retry_on_missing_output_then_success(monkeypatch):
    # First response missing output_text, second has it
    dummy = DummyClient([DummyResp(output_text=None), DummyResp(output_text="Fixed")])
    monkeypatch.setattr(ai_client, "_client", dummy)
    res = ai_client.request([{"role":"user","content":"Explain"}])
    assert res["output_text"] == "Fixed"
    # Two calls: original + retry
    assert len(dummy.calls) == 2
    # Retry should force low effort and increased max_output_tokens >= original
    first, second = dummy.calls
    assert first["reasoning"]["effort"] in ("low","medium","high")
    assert second["reasoning"]["effort"] == "low"
    assert second["max_output_tokens"] >= first["max_output_tokens"]

class HardError(Exception):
    status_code = 500

class NotFoundError(Exception):
    status_code = 404

class ShapeError(Exception):
    pass

def test_fallback_on_hard_error(monkeypatch):
    # First call raises 500, second returns success from fallback model
    dummy = DummyClient([HardError("server error"), DummyResp(output_text="Hi", model="gpt-4o-2025-08-07")])
    monkeypatch.setattr(ai_client, "_client", dummy)
    res = ai_client.request([{"role":"user","content":"Ping"}])
    assert res["output_text"] == "Hi"
    assert res["used_fallback"] is True
    assert dummy.calls[0]["model"] == "gpt-5.1"
    assert dummy.calls[1]["model"] == "gpt-4o"

@pytest.mark.parametrize("exc", [NotFoundError("model_not_found"), HardError("500"),])
def test_fallback_conditions(monkeypatch, exc):
    dummy = DummyClient([exc, DummyResp(output_text="Ok", model="gpt-4o")])
    monkeypatch.setattr(ai_client, "_client", dummy)
    res = ai_client.request([{"role":"user","content":"Test"}])
    assert res["used_fallback"] is True
    assert res["model"].startswith("gpt-4o")


def test_no_fallback_on_shape_error(monkeypatch):
    dummy = DummyClient([ShapeError("invalid param"), DummyResp(output_text="Should not be used")])
    monkeypatch.setattr(ai_client, "_client", dummy)
    res = ai_client.request([{"role":"user","content":"Bad"}])
    # Should NOT fallback; shape error returned
    assert res["output_text"] == ""
    assert res["used_fallback"] is False
    assert "invalid param" in res["error"]
