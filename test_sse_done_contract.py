import json
import ai_client
import app as flask_app
from flask import Response

app = flask_app.app

# Contract: SSE done event must include documented fields
# Fields: model, resp_id, usage.input_tokens, usage.output_tokens, fallback, latency_ms, breaker_state, backoff_ms

def parse_events(resp: Response):
    body = b"".join(resp.response).decode('utf-8')
    blocks = [b for b in body.strip().split('\n\n') if b.strip()]
    events = []
    for block in blocks:
        ev=None; data=[]
        for line in block.split('\n'):
            if line.startswith('event:'):
                ev=line[len('event:'):].strip()
            elif line.startswith('data:'):
                data.append(line[len('data:'):].strip())
        if ev:
            events.append((ev,'\n'.join(data)))
    return events


def test_sse_done_contract(monkeypatch):
    monkeypatch.setenv('OPENAI_STREAM_RESPONSES','true')
    def fake_stream(messages, **kwargs):
        yield ('delta','Hi')
        yield ('done', {'model':'gpt-5','id':'resp_contract','usage':{'input_tokens':10,'output_tokens':2}})
    monkeypatch.setattr(ai_client, 'request_stream', fake_stream)
    with app.test_client() as c:
        resp = c.post('/chat', json={'message':'Hello','page':'general'}, headers={'Accept':'text/event-stream'})
        assert resp.status_code == 200
        events = parse_events(resp)
    done_payloads = [json.loads(d) for e,d in events if e=='done']
    assert len(done_payloads)==1
    p = done_payloads[0]
    for key in ['model','resp_id','usage','fallback','latency_ms','breaker_state','backoff_ms']:
        assert key in p, f"Missing field {key} in SSE done payload"
    assert 'input_tokens' in p['usage'] and 'output_tokens' in p['usage']
