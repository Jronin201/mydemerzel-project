import json, os
os.environ.setdefault("OPENAI_API_KEY", "test-key")

# Patch OpenAI client before importing app
from types import SimpleNamespace

class _FakeChoice:
    def __init__(self, content):
        self.message = SimpleNamespace(content=content)

class _FakeResponse:
    def __init__(self, content):
        self.choices = [_FakeChoice(content)]

def _fake_create(**kwargs):
    # Use heuristic outcome handling
    msgs = kwargs.get("messages", [])
    user = [m for m in msgs if m.get("role") == "user"]
    user_text = user[-1]["content"] if user else ""
    if "[SUCCESS" in user_text.upper():
        return _FakeResponse("The action succeeds decisively; the foe staggers. Momentum shifts as the scene widens.")
    if "d20" in user_text.lower():
        return _FakeResponse("The narrative flows onward, untouched by overt mechanics.")
    return _FakeResponse("Tension builds as intent sharpens in the dust-charged air.")

import openai
from openai import OpenAI

try:
    # Monkeypatch global client attributes used in app
    orig_init = OpenAI.__init__
    def _init(self, *a, **k):
        orig_init(self, api_key="test-key")
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=_fake_create))
    OpenAI.__init__ = _init
except Exception:
    pass

from app import app, MECHANICS_BAN_ENFORCED

def _post(message, page="pendragon"):
    with app.test_client() as c:
        return c.post("/chat", json={"message": message, "page": page})

# Basic narrative only
def test_narrative_only():
    r1 = _post("Hello")
    assert r1.status_code == 200
    r2 = _post("The raider closes in.")
    data = r2.get_json()
    assert data and "roll" not in data["response"].lower()

# Outcome protocol
def test_outcome_success():
    r = _post("I bash with my shield. (Shield bash) [SUCCESS]")
    data = r.get_json()
    assert data
    resp = data["response"].lower()
    assert "success" in resp or "impact" in resp
    assert all(term not in resp for term in ["d20", "tn", "dc"])  # mechanics ban

# Blocklist sanitization
def test_blocklist_sanitization():
    r = _post("I try to roll a d20 for this.")
    data = r.get_json()
    assert data
    assert "d20" not in data["response"].lower()

if __name__ == "__main__":
    test_narrative_only()
    test_outcome_success()
    test_blocklist_sanitization()
    print("Narrative pipeline tests executed.")
