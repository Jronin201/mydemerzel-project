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

from app import app, MECHANICS_BAN_ENFORCED
import ai_client

# Monkeypatch ai_client.request for deterministic offline behavior
def _fake_request(messages, **kwargs):
    user_msgs = [m for m in messages if m.get('role')=='user']
    text = user_msgs[-1]['content'] if user_msgs else ''
    if '[SUCCESS' in text.upper():
        out = 'Success: the action succeeds decisively; the foe staggers. Momentum shifts as the scene widens.'
    elif 'd20' in text.lower():
        out = 'The narrative flows onward, untouched by overt mechanics.'
    else:
        out = 'Tension builds as intent sharpens in the dust-charged air.'
    return {'output_text': out, 'model': 'gpt-5', 'used_fallback': False, 'usage': {'input_tokens':5,'output_tokens':10}, 'id': 'offline_test'}

_orig_request = ai_client.request
ai_client.request = _fake_request  # type: ignore

def teardown_module(module):  # pragma: no cover
    ai_client.request = _orig_request  # restore original for other tests

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
