import requests
from openai import OpenAI
from anthropic import Anthropic

from app import config


def _build_messages(history, user_message):
    messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})
    return messages


def query_openai(history, user_message):
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    messages = _build_messages(history, user_message)
    response = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=messages,
    )
    return response.choices[0].message.content


def query_anthropic(history, user_message):
    client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    # Anthropic uses system as a top-level param, not in messages
    chat_messages = []
    chat_messages.extend(history)
    chat_messages.append({"role": "user", "content": user_message})
    response = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=1024,
        system=config.SYSTEM_PROMPT,
        messages=chat_messages,
    )
    return response.content[0].text


def query_ollama(history, user_message):
    messages = _build_messages(history, user_message)
    resp = requests.post(
        f"{config.OLLAMA_URL}/api/chat",
        json={
            "model": config.OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
        },
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"]


PROVIDERS = {
    "openai": query_openai,
    "anthropic": query_anthropic,
    "ollama": query_ollama,
}


def query(history, user_message):
    provider = config.AI_PROVIDER.lower()
    if provider not in PROVIDERS:
        return f"Unknown AI provider: {provider}. Use openai, anthropic, or ollama."
    return PROVIDERS[provider](history, user_message)
