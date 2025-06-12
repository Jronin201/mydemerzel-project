import token_counter


def test_count_tokens_basic():
    messages = [
        {"role": "system", "content": "Hello"},
        {"role": "user", "content": "Hi there"},
    ]
    count = token_counter.count_tokens(messages)
    assert isinstance(count, int)
    assert count > 0
