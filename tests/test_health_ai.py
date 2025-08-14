import os, sys, pytest
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import ai_client
from app import app

class DummyUsage:
    def __init__(self, input_tokens=3, output_tokens=2):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.total_tokens = input_tokens + output_tokens

class DummyResp:
    def __init__(self, output_text=None, model="gpt-5-2025-08-07", rid="resp_health", usage=None):
        self.output_text = output_text
        self.model = model
        self.id = rid
        self.usage = usage or DummyUsage()

class DummyClient:
    def __init__(self, resp):
        self.resp = resp
        class RespNS:
            def __init__(self, outer):
                self.outer = outer
            def create(self, **kwargs):
                return self.outer.resp
        self.responses = RespNS(self)

class HardError(Exception):
    status_code = 500


def test_health_ai_ok(monkeypatch):
    dummy = DummyClient(DummyResp(output_text="ok"))
    monkeypatch.setattr(ai_client, "_client", dummy)
    with app.test_client() as c:
        r = c.get("/health/ai")
        assert r.status_code == 200
        data = r.get_json()
        assert data["ok"] is True
        assert data["model"].startswith("gpt-5")


def test_health_ai_failure(monkeypatch):
    class FailClient:
        class RespNS:
            def create(self, **kwargs):
                raise HardError("server boom")
        def __init__(self):
            self.responses = self.RespNS()
    monkeypatch.setattr(ai_client, "_client", FailClient())
    with app.test_client() as c:
        r = c.get("/health/ai")
        assert r.status_code == 503
        data = r.get_json()
        assert data["ok"] is False
        assert "error" in data
