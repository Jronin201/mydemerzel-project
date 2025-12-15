import ai_client, random, time as real_time

class HardErr(Exception):
    def __init__(self, status):
        self.status_code=status
        super().__init__(f"{status} error")

class DummyResp:
    def __init__(self, text='ok', rid='id', model='gpt-5.2'):
        self.output_text=text
        self.id=rid
        self.model=model
        class U: pass
        u=U(); u.input_tokens=1; u.output_tokens=2; u.total_tokens=3
        self.usage=u


def test_backoff_retries_once_then_fallback(monkeypatch, capsys):
    ai_client.reset_circuit()
    # deterministic jitter
    monkeypatch.setattr(random, 'uniform', lambda a,b: 137.0)
    slept = {'ms':0}
    monkeypatch.setattr(ai_client, 'AI_BACKOFF_ENABLED', True)
    def fake_sleep(sec):
        slept['ms'] += int(sec*1000)
    monkeypatch.setattr(ai_client.time, 'sleep', fake_sleep)
    state={'calls':0}
    def fake_create(**kwargs):
        model=kwargs['model']
        if model.startswith('gpt-5'):
            state['calls']+=1
            if state['calls']<=2:
                raise HardErr(429)
            return DummyResp(rid='primary_success')
        return DummyResp(rid='fb', model=model)
    class DummyClient:
        class Responses:
            @staticmethod
            def create(**kwargs):
                return fake_create(**kwargs)
        responses=Responses()
    monkeypatch.setattr(ai_client, '_client', DummyClient())
    res = ai_client.request([{'role':'user','content':'x'}], req_id='back1')
    # After first 429 and retry 429 fallback used => used_fallback True
    assert res['used_fallback'] is True
    assert slept['ms'] == 137  # one backoff


def test_backoff_retry_success(monkeypatch):
    ai_client.reset_circuit()
    monkeypatch.setattr(random, 'uniform', lambda a,b: 111.0)
    monkeypatch.setattr(ai_client, 'AI_BACKOFF_ENABLED', True)
    slept={'ms':0}
    def fake_sleep(sec):
        slept['ms'] += int(sec*1000)
    monkeypatch.setattr(ai_client.time, 'sleep', fake_sleep)
    state={'calls':0}
    def fake_create(**kwargs):
        model=kwargs['model']
        if model.startswith('gpt-5'):
            state['calls']+=1
            if state['calls']==1:
                # use 429 to trigger backoff inline retry (no fallback)
                raise HardErr(429)
            return DummyResp(rid='primary_ok')
        return DummyResp(rid='fb', model=model)
    class DummyClient:
        class Responses:
            @staticmethod
            def create(**kwargs):
                return fake_create(**kwargs)
        responses=Responses()
    monkeypatch.setattr(ai_client, '_client', DummyClient())
    res = ai_client.request([{'role':'user','content':'y'}], req_id='back2')
    assert res['used_fallback'] is False
    assert slept['ms'] == 111
    assert res['backoff_ms'] == 111
