from typing import Any

import requests
from smolagents import CodeAgent, LiteLLMModel

from .config import get_settings
from .finam_tool import FinamAPITool


def call_llm(messages: list[dict[str, str]], temperature: float = 0.2, max_tokens: int | None = None) -> dict[str, Any]:
    """Простой вызов LLM без tools"""
    s = get_settings()
    payload: dict[str, Any] = {
        "model": s.openrouter_model,
        "messages": messages,
        "temperature": temperature,
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


def call_llm_with_tools(
    messages: list[dict[str, str]],
    temperature: float = 0.2,
    max_tokens: int | None = None,
    tools: list | None = None,
) -> dict[str, Any]:
    """
    Вызов LLM с использованием smolagents и tools.

    Args:
        messages: История сообщений для LLM
        temperature: Температура генерации
        max_tokens: Максимальное количество токенов
        tools: Список инструментов для использования агентом

    Returns:
        dict: Ответ в формате совместимом с OpenAI API с дополнительными полями:
            - 'agent_logs': логи выполнения агента
            - 'tool_calls': список вызовов инструментов
    """
    s = get_settings()

    # Создаем модель LiteLLM, которая работает с OpenRouter
    model = LiteLLMModel(
        model_id=s.openrouter_model,
        api_base=s.openrouter_base,
        api_key=s.openrouter_api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    # Используем предоставленные инструменты или создаем Finam API tool по умолчанию
    agent_tools = tools if tools is not None else [FinamAPITool()]

    # Создаем агента
    agent = CodeAgent(tools=agent_tools, model=model, max_steps=5)

    # Извлекаем задачу из последнего сообщения пользователя
    task = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            task = msg.get("content", "")
            break

    if not task:
        task = messages[-1].get("content", "") if messages else ""

    # Запускаем агента
    try:
        result = agent.run(task, return_full_result=True)

        # Форматируем ответ в стиле OpenAI API
        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": str(result.output) if hasattr(result, "output") else str(result),
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 0,  # smolagents не предоставляет детальную статистику
                "completion_tokens": 0,
                "total_tokens": 0,
            },
            # Дополнительные поля для отладки
            "agent_logs": result.logs if hasattr(result, "logs") else [],
            "tool_calls": _extract_tool_calls(result),
        }
    except Exception as e:
        # В случае ошибки возвращаем fallback ответ
        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": f"Ошибка при выполнении: {e}",
                    },
                    "finish_reason": "error",
                }
            ],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "error": str(e),
        }


def _extract_tool_calls(result: Any) -> list[dict[str, Any]]:  # noqa: ANN401
    """
    Извлекает информацию о вызовах инструментов из результата агента

    Args:
        result: Результат выполнения агента

    Returns:
        list: Список вызовов инструментов с их результатами
    """
    tool_calls = []

    if not hasattr(result, "logs"):
        return tool_calls

    for step in result.logs:
        if hasattr(step, "tool_calls") and step.tool_calls:
            for tool_call in step.tool_calls:
                tool_calls.append(
                    {
                        "tool_name": tool_call.name if hasattr(tool_call, "name") else "unknown",
                        "arguments": tool_call.arguments if hasattr(tool_call, "arguments") else {},
                        "result": tool_call.result if hasattr(tool_call, "result") else None,
                    }
                )

    return tool_calls
