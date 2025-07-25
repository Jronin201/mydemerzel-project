def count_tokens(messages):
    """Approximate token counting without ``tiktoken``.

    The real project uses the ``tiktoken`` library to get accurate counts,
    but that requires downloading model data at runtime. In offline test
    environments this fails, so here we simply count whitespace separated
    words for each message. The result is good enough for unit testing.
    """

    num_tokens = 0
    for message in messages:
        for value in message.values():
            num_tokens += len(str(value).split())
    return num_tokens
