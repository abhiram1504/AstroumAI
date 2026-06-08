import tiktoken

_encoder = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    return len(_encoder.encode(text))

def count_three_sources(system_prompt: str, context_string: str, user_reserve: int = 200) -> dict:
    system_tokens = count_tokens(system_prompt)
    context_tokens = count_tokens(context_string)
    total = system_tokens + context_tokens + user_reserve

    return {
        "system_prompt_tokens": system_tokens,
        "context_tokens": context_tokens,
        "user_message_tokens": user_reserve,
        "total": total,
        "budget": 4000,
        "remaining": 4000 - total,
        "over_budget": total > 4000
    }