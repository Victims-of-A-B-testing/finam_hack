from typing import Any

import requests

from .config import get_settings
from .smolagents_wrapper import create_smolagent


def call_llm(messages: list[dict[str, str]], temperature: float = 0.2, max_tokens: int | None = None) -> dict[str, Any]:
    """Простой вызов LLM без tools"""
    s = get_settings()
    payload: dict[str, Any] = {
        "model": s.openrouter_model,
        "messages": messages,
        "temperature": temperature,
        # "plugins": [{ "id": "web" }]
    }
    if max_tokens:
        payload["max_tokens"] = max_tokens
        
    r = requests.post(
        f"{s.openrouter_base}/chat/completions",
        headers={
            "Authorization": f"Bearer {s.openrouter_api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )
    r.raise_for_status()
    return r.json()

def call_smolagents(messages: list[dict[str, str]], temperature: float = 0.2, max_tokens: int | None = None) -> dict[str, Any]:
    """Простой вызов LLM без tools через smolagents"""
    s = get_settings()
    agent = create_smolagent(s)
    r = agent.run(messages[-1]["content"], return_full_result=True)
    return r