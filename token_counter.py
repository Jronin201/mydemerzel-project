import tiktoken

def count_tokens(messages, model="gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    tokens_per_message = 4  # OpenAI standard for chat messages
    tokens_per_name = -1    # If name exists in message, adjust count

    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    return num_tokens + 2  # Includes priming tokens
