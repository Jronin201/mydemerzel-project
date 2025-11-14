import re, json, io, sys
import app as flask_app

app = flask_app.app

def test_non_stream_latency_log(monkeypatch, capsys):
    # ensure streaming disabled
    monkeypatch.delenv('OPENAI_STREAM_RESPONSES', raising=False)
    # force verbose logging
    monkeypatch.setenv('OBS_VERBOSE','true')
    # patch ai_client.request to return simple response quickly
    import ai_client
    def fake_request(messages, **kwargs):
        # mimic ai_client.request return structure with id/backoff_ms for logging
        return {
            'output_text':'Hello',
            'usage': {'input_tokens':5,'output_tokens':2},
            'model':'gpt-5.1',
            'id':'resp_lat',
            'backoff_ms': '-',
            'used_fallback': False
        }
    monkeypatch.setattr(ai_client,'request', fake_request)
    with app.test_client() as c:
        r = c.post('/chat', json={'message':'Hi','page':'general'})
        assert r.status_code == 200
    # Force flush
    print('', flush=True)
    # capture logs
    captured = capsys.readouterr().out
    # find CHAT line
    lines = [ln for ln in captured.splitlines() if ln.startswith('[CHAT]')]
    assert lines, 'Expected a [CHAT] log line'
    line = lines[0]
    assert 'openai.latency_ms=' in line, 'Latency not logged'
    assert 'breaker.state=' in line
    assert 'backoff.ms=' in line
    assert 'req.id=' in line
    # ensure latency is integer
    m = re.search(r'openai.latency_ms=(\d+)', line)
    assert m, 'Latency pattern missing'
    assert int(m.group(1)) >= 0
