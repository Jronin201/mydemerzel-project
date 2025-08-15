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
        # Add baseline flags presence (may be absent or False)
        assert 'near_cap' in meta and 'truncated' in meta


    def test_near_cap_non_stream(monkeypatch):
        monkeypatch.setenv('OPENAI_STREAM_RESPONSES','false')
        near_cap_tokens = int(ai_client.OPENAI_MAX_OUTPUT_TOKENS * 0.95)
        txt = 'X ' * near_cap_tokens
        def fake_request(messages, **kwargs):
            return {
                'output_text': txt,
                'model': 'gpt-5-nearcap',
                'used_fallback': False,
                'id': 'resp_near_cap',
                'usage': {'input_tokens': 1000, 'output_tokens': near_cap_tokens, 'total_tokens': near_cap_tokens+1000},
                'near_cap': True,
                'truncated': False,
                'backoff_ms': 0,
                'breaker_state': 'closed'
            }
        monkeypatch.setattr(ai_client, 'request', fake_request)
        with app.test_client() as c:
            resp = c.post('/chat', json={'message':'Generate near cap','page':'general'})
            data = resp.get_json()
            assert data['usage']['output_tokens'] == near_cap_tokens
            assert data.get('near_cap') is True
            assert data.get('truncated') is False


    def test_truncated_non_stream(monkeypatch):
        monkeypatch.setenv('OPENAI_STREAM_RESPONSES','false')
        cap = ai_client.OPENAI_MAX_OUTPUT_TOKENS
        txt = 'Y ' * cap
        def fake_request(messages, **kwargs):
            return {
                'output_text': txt,
                'model': 'gpt-5-trunc',
                'used_fallback': False,
                'id': 'resp_trunc',
                'usage': {'input_tokens': 500, 'output_tokens': cap, 'total_tokens': cap+500},
                'near_cap': True,
                'truncated': True,
                'backoff_ms': 0,
                'breaker_state': 'closed'
            }
        monkeypatch.setattr(ai_client, 'request', fake_request)
        with app.test_client() as c:
            resp = c.post('/chat', json={'message':'Generate truncated','page':'general'})
            data = resp.get_json()
            assert data['usage']['output_tokens'] == cap
            assert data.get('truncated') is True


    def test_near_cap_streaming(monkeypatch):
        monkeypatch.setenv('OPENAI_STREAM_RESPONSES','true')
        near_cap_tokens = int(ai_client.OPENAI_MAX_OUTPUT_TOKENS * 0.95)
        def fake_stream(messages, **kwargs):
            for i in range(near_cap_tokens):
                if i < 10:  # keep test runtime small by limiting actual yielded tokens
                    yield ('delta','Z')
            yield ('done', {'model':'gpt-5-nearcap','id':'resp_nearcap_stream','usage':{'input_tokens':1000,'output_tokens':near_cap_tokens},'near_cap':True,'truncated':False})
        monkeypatch.setattr(ai_client, 'request_stream', fake_stream)
        with app.test_client() as c:
            resp = c.post('/chat', json={'message':'Stream near cap','page':'general'}, headers={'Accept':'text/event-stream'})
            body = b''
            for part in resp.response:
                if isinstance(part, str):
                    part = part.encode('utf-8')
                body += part
            body = body.decode('utf-8')
            assert 'near_cap' in body


    def test_truncated_streaming(monkeypatch):
        monkeypatch.setenv('OPENAI_STREAM_RESPONSES','true')
        cap = ai_client.OPENAI_MAX_OUTPUT_TOKENS
        def fake_stream(messages, **kwargs):
            for i in range(10):
                yield ('delta','Q')
            yield ('done', {'model':'gpt-5-trunc','id':'resp_trunc_stream','usage':{'input_tokens':100,'output_tokens':cap},'near_cap':True,'truncated':True})
        monkeypatch.setattr(ai_client, 'request_stream', fake_stream)
        with app.test_client() as c:
            resp = c.post('/chat', json={'message':'Stream truncated','page':'general'}, headers={'Accept':'text/event-stream'})
            body = b''
            for part in resp.response:
                if isinstance(part, str):
                    part = part.encode('utf-8')
                body += part
            body = body.decode('utf-8')
            assert 'truncated' in body
        assert meta['usage']['output_tokens'] == 5000
        assert meta['fallback'] is False
