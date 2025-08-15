import ai_client


def test_history_role_type_mapping(monkeypatch):
    messages = [
        {"role":"system","content":"You are a guide."},
        {"role":"user","content":"Hi"},
        {"role":"assistant","content":"Hello!"},
        {"role":"user","content":"How are you?"},
    ]
    converted = ai_client._build_responses_input(messages)  # noqa: SLF001 (intentional test of internal)
    assert len(converted) == 4
    assert converted[0]['content'][0]['type'] == 'input_text'
    assert converted[1]['content'][0]['type'] == 'input_text'
    assert converted[2]['content'][0]['type'] == 'output_text'
    assert converted[3]['content'][0]['type'] == 'input_text'
