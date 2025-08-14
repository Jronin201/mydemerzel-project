import json, re
import ai_client
import app as flask_app
from flask import Response

app = flask_app.app

# Helper to parse SSE events

def parse_sse(resp: Response):
    body = b"".join(resp.response)
    text = body.decode('utf-8')
    blocks = [b for b in text.split('\n\n') if b.strip()]
    events = []
    for block in blocks:
        ev = None
        data_lines = []
        for line in block.split('\n'):
            if line.startswith('event:'):
                ev = line[len('event:'):].strip()
            elif line.startswith('data:'):
                data_lines.append(line[len('data:'):].strip())
        if ev:
            events.append((ev, '\n'.join(data_lines)))
    return events

class DummyEvent:
    def __init__(self, type_, delta=None, model=None, usage=None, id_=None):
        self.type = type_
        self.delta = delta
        self.model = model
        self.usage = usage
        self.id = id_


def test_abort_during_token(monkeypatch, capsys):
    monkeypatch.setenv('OPENAI_STREAM_RESPONSES','true')
    # Simulate stream producing two deltas then completion
    def fake_stream(messages, **kwargs):
        yield ('delta', 'A')
        yield ('delta', 'B')  # second write will raise
        yield ('done', {'model':'gpt-5','id':'resp_abort_tok','usage':{'input_tokens':10,'output_tokens':2}})
    monkeypatch.setattr(ai_client, 'request_stream', fake_stream)
    # Monkeypatch sse writer inside app by wrapping Response after generation not trivial; instead simulate BrokenPipe on second token by patching the sse function? Simpler: patch flask Response to raise on second write -> we cannot easily; fallback: mimic raising in route by raising in generator after yielding first token
    calls = {'count':0}
    orig_request_stream = ai_client.request_stream
    def wrapper(messages, **kwargs):
        for kind, payload in orig_request_stream(messages, **kwargs):
            if kind == 'delta':
                calls['count'] += 1
                if calls['count'] == 2:
                    raise BrokenPipeError('client disconnected')
            yield (kind, payload)
    monkeypatch.setattr(ai_client, 'request_stream', wrapper)
    with app.test_client() as c:
        resp = c.post('/chat', json={'message':'Hi','page':'general'}, headers={'Accept':'text/event-stream'})
        events = parse_sse(resp)
    # Expect only first token then abort (ping may exist)
    token_events = [d for e,d in events if e=='token']
    assert token_events == ['A']
    done_events = [d for e,d in events if e=='done']
    assert not done_events, 'No done event expected after abort'
    out = capsys.readouterr().out
    abort_lines = [ln for ln in out.splitlines() if 'stream.aborted=true' in ln]
    assert len(abort_lines) == 1


def test_abort_during_heartbeat(monkeypatch, capsys):
    monkeypatch.setenv('OPENAI_STREAM_RESPONSES','true')
    flask_app.app.config['STREAM_HEARTBEAT_INTERVAL'] = 0.01
    # Stream yields one delta then long gap; we inject BrokenPipe on ping by raising when heartbeat triggered
    def fake_stream(messages, **kwargs):
        yield ('delta', 'X')
        # no more events (simulate waiting)
        yield ('done', {'model':'gpt-5','id':'resp_abort_hb','usage':{'input_tokens':5,'output_tokens':1}})
    monkeypatch.setattr(ai_client, 'request_stream', fake_stream)
    # Patch time to force heartbeat attempt with failure via raising in sse send. We'll simulate by raising after first delta in generator on subsequent iteration by wrapping again.
    sent = {'ping':False}
    orig_request_stream = ai_client.request_stream
    def wrapper(messages, **kwargs):
        for idx,(kind,payload) in enumerate(orig_request_stream(messages, **kwargs)):
            if kind=='delta':
                yield (kind,payload)
            elif kind=='done':
                # emulate long wait so heartbeat triggers and fails
                if not sent['ping']:
                    sent['ping']=True
                    raise BrokenPipeError('client disconnected on heartbeat')
                yield (kind,payload)
    monkeypatch.setattr(ai_client, 'request_stream', wrapper)
    with app.test_client() as c:
        resp = c.post('/chat', json={'message':'Hi','page':'general'}, headers={'Accept':'text/event-stream'})
        events = parse_sse(resp)
    token_events = [d for e,d in events if e=='token']
    assert token_events == ['X']
    done_events = [d for e,d in events if e=='done']
    assert not done_events
    out = capsys.readouterr().out
    abort_lines = [ln for ln in out.splitlines() if 'stream.aborted=true' in ln]
    assert len(abort_lines) == 1
