import ai_client, types
import builtins
import time as real_time

class HardErr(Exception):
    def __init__(self, status):
        self.status_code = status
        super().__init__(f"{status} server error")

def make_monotonic(start=0.0):
    state = {'t': start}
    def mono():
        return state['t']
    def advance(dt):
        state['t'] += dt
    return mono, advance


def setup_client(monkeypatch, fail_primary_times, mono):
    # mutable counters
    state = {'failures':0}
    class DummyResp:
        def __init__(self, text='hello', rid='id', model='gpt-5'):
            self.output_text=text
            self.id=rid
            self.model=model
            class U: pass
            u=U(); u.input_tokens=1; u.output_tokens=1; u.total_tokens=2
            self.usage=u
    def fake_create(**kwargs):
        model = kwargs.get('model')
        if model.startswith('gpt-5') and state['failures'] < fail_primary_times:
            state['failures'] += 1
            raise HardErr(500)
        return DummyResp(rid=f"resp_{state['failures']}", model=model)
    class DummyClient:
        class Responses:
            @staticmethod
            def create(**kwargs):
                return fake_create(**kwargs)
        responses = Responses()
    monkeypatch.setattr(ai_client, '_client', DummyClient())
    monkeypatch.setattr(ai_client, '_now', mono)
    return state


def test_breaker_opens_on_three(monkeypatch):
    mono, advance = make_monotonic()
    setup_client(monkeypatch, fail_primary_times=3, mono=mono)
    monkeypatch.setattr(ai_client, 'AI_BACKOFF_ENABLED', False)
    for i in range(3):
        ai_client.request([{'role':'user','content':'hi'}], req_id=f'r{i}')
        assert len(ai_client._circuit_failures) == i+1
    st = ai_client.circuit_state()
    assert st['state'] == 'open'

