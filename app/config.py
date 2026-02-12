import os

from dotenv import load_dotenv

load_dotenv()


def get(key, default=None):
    return os.environ.get(key, default)


AI_PROVIDER = get("AI_PROVIDER", "openai")

OPENAI_API_KEY = get("OPENAI_API_KEY", "")
OPENAI_MODEL = get("OPENAI_MODEL", "gpt-4o-mini")

ANTHROPIC_API_KEY = get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

OLLAMA_URL = get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = get("OLLAMA_MODEL", "llama3.2")

TWILIO_ACCOUNT_SID = get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = get("TWILIO_AUTH_TOKEN", "")

SYSTEM_PROMPT = get(
    "SYSTEM_PROMPT",
    "You are a helpful assistant answering questions via SMS. "
    "Keep responses concise and under 300 characters when possible. "
    "No markdown formatting. Plain text only.",
)

HOST = get("HOST", "0.0.0.0")
PORT = int(get("PORT", "5000"))

MAX_HISTORY = int(get("MAX_HISTORY", "10"))
