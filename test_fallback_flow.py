import os
import types
from unittest.mock import patch

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
    import ai_client, importlib
    importlib.reload(ai_client)
    # Script sequence: primary hard error then fallback success
    class HardErr(Exception):
        status_code = 500
    # Simulate _client.responses.create raising once (primary) then fallback success
    import types
    class DummyResp:
        def __init__(self, text, model):
            self.output_text=text; self.model=model; self.id='fb'
            class U: ...
            u = types.SimpleNamespace(input_tokens=3, output_tokens=7, total_tokens=10)
            self.usage = u
    class HardErr(Exception):
        status_code=500
    seq=[HardErr('boom'), DummyResp('Fallback OK','gpt-4o')]
    class DummyClient:
        class Responses:
            def __init__(self, seq): self.seq=seq
            def create(self, **kwargs):
                item=self.seq.pop(0)
                if isinstance(item, Exception):
                    raise item
                # override model to simulate fallback model selected
                item.model=kwargs['model']
                return item
        def __init__(self, seq): self.responses=DummyClient.Responses(seq)
    monkeypatch.setattr(ai_client,'_client', DummyClient(seq))
    res = ai_client.request([{"role":"user","content":"Explain combat"}])
    assert res['output_text'] == 'Fallback OK'
    assert res['used_fallback'] is True
