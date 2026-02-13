import requests
from openai import OpenAI
from anthropic import Anthropic
from google import genai
from google.genai import types

from app import config


def _build_messages(history, user_message, system_prompt=None):
    messages = [{"role": "system", "content": system_prompt or config.SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})
    return messages


def query_openai(history, user_message, system_prompt=None):
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    messages = _build_messages(history, user_message, system_prompt)
    response = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=messages,
    )
    return response.choices[0].message.content


def query_anthropic(history, user_message, system_prompt=None):
    client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    # Anthropic uses system as a top-level param, not in messages
    chat_messages = []
    chat_messages.extend(history)
    chat_messages.append({"role": "user", "content": user_message})
    response = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=1024,
        system=system_prompt or config.SYSTEM_PROMPT,
        messages=chat_messages,
    )
    return response.content[0].text


def query_gemini(history, user_message, system_prompt=None):
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    # Build contents list with conversation history
    contents = []
    for msg in history:
        role = "model" if msg["role"] == "assistant" else msg["role"]
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(msg["content"])],
            )
        )
    contents.append(
        types.Content(role="user", parts=[types.Part.from_text(user_message)])
    )
    response = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt or config.SYSTEM_PROMPT,
        ),
    )
    return response.text


def query_ollama(history, user_message, system_prompt=None):
    messages = _build_messages(history, user_message, system_prompt)
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
    "gemini": query_gemini,
    "ollama": query_ollama,
}


def query(history, user_message, system_prompt=None):
    provider = config.AI_PROVIDER.lower()
    if provider not in PROVIDERS:
        return f"Unknown AI provider: {provider}. Use openai, anthropic, gemini, or ollama."
    return PROVIDERS[provider](history, user_message, system_prompt)
