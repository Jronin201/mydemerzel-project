import json
import re
from flask import Response
import ai_client
import app as flask_app

# NOTE: Placed at repo root per instructions; moved under tests/ if needed.

app = flask_app.app

class DummyEvent:
    def __init__(self, type_, delta=None, model=None, usage=None, id_=None, error=None):
        self.type = type_
        self.delta = delta
        self.model = model
        self.usage = usage
        self.id = id_
        self.error = error


def iter_sse(resp: Response):
    body = b"".join(resp.response)
    text = body.decode('utf-8')
    events = []
    raw_blocks = [b for b in text.strip().split('\n\n') if b.strip()]
    for block in raw_blocks:
        lines = block.split('\n')
        ev = None
        data_lines = []
        for line in lines:
            if line.startswith('event:'):
                ev = line[len('event:'):].strip()
            elif line.startswith('data:'):
                data_lines.append(line[len('data:'):].strip())
        data = '\n'.join(data_lines)
        events.append((ev, data))
    return events


def test_stream_happy(monkeypatch):
    # Arrange streaming env
    monkeypatch.setenv('OPENAI_STREAM_RESPONSES', 'true')
    deltas = ["Hello", ", ", "world", "!"]
    def fake_stream(messages, **kwargs):
        # yield delta events then done
        yield ("delta", deltas[0])
        yield ("delta", deltas[1])
        yield ("delta", deltas[2])
        yield ("delta", deltas[3])
        yield ("done", {"model":"gpt-5","id":"resp_123","usage":{"input_tokens":42,"output_tokens":10}})
    monkeypatch.setattr(ai_client, 'request_stream', fake_stream)
    with app.test_client() as c:
        resp = c.post('/chat', json={"message":"Test","page":"general"}, headers={'Accept':'text/event-stream'})
        assert resp.status_code == 200
        events = iter_sse(resp)
        token_text = ''.join([d for e,d in events if e=='token'])
        # Allow either with or without space depending on delta join
        assert token_text.replace(' ', '') == 'Hello,world!'
        done_payload = json.loads([d for e,d in events if e=='done'][0])
        assert done_payload['model'] == 'gpt-5'
        assert done_payload['fallback'] is False


def test_stream_reasoning_only_retry(monkeypatch):
    monkeypatch.setenv('OPENAI_STREAM_RESPONSES', 'true')
    attempts = {'count':0}
    def fake_stream(messages, **kwargs):
        attempts['count'] += 1
        if attempts['count'] == 1:
            # no deltas, reasoning only -> done empty
            yield ("done", {"model":"gpt-5","id":"resp_a","usage":{"input_tokens":10,"output_tokens":0}})
        else:
            yield ("delta", "Final")
            yield ("done", {"model":"gpt-5","id":"resp_b","usage":{"input_tokens":15,"output_tokens":5}})
    monkeypatch.setattr(ai_client, 'request_stream', fake_stream)
    with app.test_client() as c:
        resp = c.post('/chat', json={"message":"Test","page":"general"}, headers={'Accept':'text/event-stream'})
        events = iter_sse(resp)
        # Expect one token after retry
        tokens = [d for e,d in events if e=='token']
        assert tokens == ['Final']
        done_payload = json.loads([d for e,d in events if e=='done'][0])
        assert done_payload['fallback'] is False
        assert attempts['count'] == 2


def test_stream_hard_error_fallback(monkeypatch):
    monkeypatch.setenv('OPENAI_STREAM_RESPONSES', 'true')
    class HardErr(Exception):
        pass
    def fake_is_hard_error(e):
        return True
    # first attempt raises
    def fake_stream(messages, **kwargs):
        raise HardErr('500 server error')
    # fallback attempt with deltas
    seq = {'used':False}
    def fake_stream_fb(messages, **kwargs):
        yield ("delta", "Hi")
        yield ("done", {"model":"gpt-4o","id":"resp_fb","usage":{"input_tokens":20,"output_tokens":3}})
    monkeypatch.setattr(ai_client, 'request_stream', fake_stream)
    # patch inside app.generate fallback call by substituting ai_client.request_stream later
    def side_effect(messages, **kwargs):
        if not seq['used']:
            seq['used']=True
            return fake_stream(messages, **kwargs)
        return fake_stream_fb(messages, **kwargs)
    monkeypatch.setattr(ai_client, 'request_stream', side_effect)
    monkeypatch.setattr(ai_client, 'is_hard_error', fake_is_hard_error)
    with app.test_client() as c:
        resp = c.post('/chat', json={"message":"Test","page":"general"}, headers={'Accept':'text/event-stream'})
        events = iter_sse(resp)
        tokens = ''.join([d for e,d in events if e=='token'])
        assert tokens == 'Hi'
        done_payload = json.loads([d for e,d in events if e=='done'][0])
        assert done_payload['fallback'] is True
        assert done_payload['model'] == 'gpt-4o'


def test_stream_heartbeat(monkeypatch):
    monkeypatch.setenv('OPENAI_STREAM_RESPONSES', 'true')
    # shorten heartbeat interval
    flask_app.app.config['STREAM_HEARTBEAT_INTERVAL'] = 0.01
    def fake_stream(messages, **kwargs):
        yield ("delta", "A")
        # simulate long gap by doing nothing (heartbeat handler triggers via time checks in route loop)
        yield ("done", {"model":"gpt-5","id":"resp_hb","usage":{"input_tokens":5,"output_tokens":1}})
    monkeypatch.setattr(ai_client, 'request_stream', fake_stream)
    with app.test_client() as c:
        resp = c.post('/chat', json={"message":"Ping","page":"general"}, headers={'Accept':'text/event-stream'})
        events = iter_sse(resp)
        # Expect at least one ping
        pings = [d for e,d in events if e=='ping']
        assert pings, 'Expected heartbeat ping events'
        done_payload = json.loads([d for e,d in events if e=='done'][0])
        assert done_payload['model'] == 'gpt-5'
        assert done_payload['fallback'] is False
