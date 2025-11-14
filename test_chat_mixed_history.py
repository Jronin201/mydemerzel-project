import json
import ai_client
import app as flask_app

app = flask_app.app


def test_chat_route_mixed_history_non_stream(monkeypatch):
    # Force non-stream behavior
    monkeypatch.setenv('OPENAI_STREAM_RESPONSES','false')

    # Stub AI client request to capture messages and return a deterministic GPT-5 style response
    def fake_request(messages, **kwargs):
        # emulate that _build_responses_input already mapped roles correctly
        # Provide usage with positive output tokens
        return {
            'output_text': 'OK response',
            'model': 'gpt-5.1-2025-08-15',
            'used_fallback': False,
            'id': 'resp_mixed_history',
            'usage': {'input_tokens': 25, 'output_tokens': 6, 'total_tokens': 31},
            'backoff_ms': 0,
            'breaker_state': 'closed'
        }
    monkeypatch.setattr(ai_client, 'request', fake_request)

    # Pre-seed session history to include system, user, assistant, user
    with app.test_client() as c:
        with c.session_transaction() as sess:
            # Simulate stored chat mode state
            sess['chat_mode'] = 'narrative'
            sess['mechanics_inactivity'] = 0
        # Seed user messages file / in-memory by simulating prior turns via direct save if available
        # Instead, include them in the posted payload under a custom key 'history' consumed for test injection.
        # Since app pulls history from persistence, we patch the history loader.
        original_loader = flask_app.load_user_messages if hasattr(flask_app,'load_user_messages') else None
        def fake_load_user_messages(username, page):
            return [
                {'role':'system','content':'System prompt active.'},
                {'role':'user','content':'Hi'},
                {'role':'assistant','content':'Hello there!'},
            ]
        monkeypatch.setattr(flask_app, 'load_user_messages', fake_load_user_messages, raising=False)
        monkeypatch.setattr(flask_app, 'get_user_messages', fake_load_user_messages, raising=False)

        resp = c.post('/chat', json={'message':'How are you?','page':'general'})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['message']
        assert data['model'].startswith('gpt-5.1-') or 'gpt-5.1' in data['model']
        assert data['fallback'] is False
        assert data['usage']['output_tokens'] > 0


def test_chat_route_mixed_history_stream(monkeypatch):
    monkeypatch.setenv('OPENAI_STREAM_RESPONSES','true')

    def fake_stream(messages, **kwargs):
        yield ('delta','O')
        yield ('delta','K')
        yield ('done', {'model':'gpt-5.1-2025-08-15','id':'resp_stream_mixed','usage':{'input_tokens':20,'output_tokens':5}})
    monkeypatch.setattr(ai_client, 'request_stream', fake_stream)

    with app.test_client() as c:
        # Patch history loader as above
        def fake_load_user_messages(username, page):
            return [
                {'role':'system','content':'System prompt active.'},
                {'role':'user','content':'Hi'},
                {'role':'assistant','content':'Hello there!'},
            ]
        monkeypatch.setattr(flask_app, 'load_user_messages', fake_load_user_messages, raising=False)
        monkeypatch.setattr(flask_app, 'get_user_messages', fake_load_user_messages, raising=False)

        resp = c.post('/chat', json={'message':'Continue','page':'general'}, headers={'Accept':'text/event-stream'})
        body = b''.join(resp.response).decode('utf-8')
        # Extract events
        blocks = [b for b in body.split('\n\n') if b.strip()]
        events = []
        for block in blocks:
            lines = block.split('\n')
            ev=None; data=[]
            for line in lines:
                if line.startswith('event:'): ev=line[len('event:'):].strip()
                elif line.startswith('data:'): data.append(line[len('data:'):].strip())
            if ev: events.append((ev,'\n'.join(data)))
        token_text = ''.join([d for e,d in events if e=='token'])
        assert token_text == 'OK'
        done_payloads = [json.loads(d) for e,d in events if e=='done']
        assert len(done_payloads)==1
        meta = done_payloads[0]
        for k in ['model','resp_id','usage','fallback','latency_ms','breaker_state','backoff_ms']:
            assert k in meta
        assert meta['fallback'] is False
        assert 'gpt-5.1' in meta['model']
