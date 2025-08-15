import json
import ai_client
import app as flask_app

app = flask_app.app


def test_long_output_non_stream(monkeypatch):
    monkeypatch.setenv('OPENAI_STREAM_RESPONSES','false')
    # Simulate ~6000 tokens output (length proxy only)
    long_text = "TOKEN " * 6000
    def fake_request(messages, **kwargs):
        return {
            'output_text': long_text,
            'model': 'gpt-5-long-test',
            'used_fallback': False,
            'id': 'resp_long_non_stream',
            'usage': {'input_tokens': 800, 'output_tokens': 6000, 'total_tokens': 6800},
            'backoff_ms': 0,
            'breaker_state': 'closed'
        }
    monkeypatch.setattr(ai_client, 'request', fake_request)
    with app.test_client() as c:
        resp = c.post('/chat', json={'message':'Generate a very long narrative','page':'general'})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['fallback'] is False
        assert 'TOKEN' in data['message']
        assert data['usage']['output_tokens'] == 6000


def test_long_output_streaming(monkeypatch):
    monkeypatch.setenv('OPENAI_STREAM_RESPONSES','true')
    # Simulate streaming many chunks
    chunks = [f"W{i} " for i in range(5000)]  # pseudo ~5k tokens
    def fake_stream(messages, **kwargs):
        for ch in chunks:
            yield ('delta', ch)
        yield ('done', {'model':'gpt-5-long-test','id':'resp_long_stream','usage':{'input_tokens':900,'output_tokens':5000}})
    monkeypatch.setattr(ai_client, 'request_stream', fake_stream)
    with app.test_client() as c:
        resp = c.post('/chat', json={'message':'Stream a very long narrative','page':'general'}, headers={'Accept':'text/event-stream'})
        assert resp.status_code == 200
        body = b''.join(resp.response).decode('utf-8')
        blocks = [b for b in body.split('\n\n') if b.strip()]
        token_events = 0
        done_payloads = []
        for block in blocks:
            ev=None; data_lines=[]
            for line in block.split('\n'):
                if line.startswith('event:'): ev=line[len('event:'):].strip()
                elif line.startswith('data:'): data_lines.append(line[len('data:'):].strip())
            if ev == 'token':
                token_events += 1
            elif ev == 'done':
                done_payloads.append(json.loads('\n'.join(data_lines)))
        assert token_events == len(chunks)
        assert len(done_payloads) == 1
        meta = done_payloads[0]
        for k in ['model','resp_id','usage','fallback','latency_ms','breaker_state','backoff_ms']:
            assert k in meta
        assert meta['usage']['output_tokens'] == 5000
        assert meta['fallback'] is False
