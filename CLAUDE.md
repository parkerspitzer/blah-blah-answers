# CLAUDE.md

## Project Overview

Blah Blah Answers is an SMS-to-AI gateway for dumb phones. Users text questions to a Twilio phone number, and the server forwards them to an AI provider (OpenAI, Anthropic, or Ollama), returning the response via SMS. Self-hostable with Docker.

## Tech Stack

- **Language:** Python 3.10+ (3.12 in Docker)
- **Web framework:** Flask 3.1
- **WSGI server:** Gunicorn 23
- **SMS:** Twilio SDK 9
- **AI providers:** OpenAI SDK 1.x, Anthropic SDK 0.x, Ollama via HTTP
- **Database:** SQLite (conversation history)
- **Config:** python-dotenv

## Project Structure

```
app/
  __init__.py      # Empty package marker
  config.py        # Environment variable loading (all settings as module-level constants)
  main.py          # Flask app factory (create_app), health endpoint, entry point
  providers.py     # AI provider abstraction (openai/anthropic/ollama query functions)
  sms.py           # SMS webhook handler (POST /sms), Twilio validation, commands
  history.py       # SQLite conversation history (thread-local connections)
```

Root files: `Dockerfile`, `docker-compose.yml`, `requirements.txt`, `.env.example`, `README.md`

## Running the App

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env  # then fill in API keys

# Run directly
python -m app.main

# Run with Docker
docker compose up -d
```

## HTTP Endpoints

- `POST /sms` — Twilio webhook for incoming SMS messages
- `GET /health` — Health check, returns `{"status": "ok", "provider": "..."}`

## Architecture & Key Patterns

- **App factory:** `create_app()` in `app/main.py` initializes Flask and registers blueprints
- **Blueprint:** SMS routes live in `sms_bp` (`app/sms.py`)
- **Provider pattern:** `PROVIDERS` dict in `app/providers.py` maps provider names to query functions. `query()` dispatches based on `config.AI_PROVIDER`
- **Message format:** All providers use `{"role": "user"/"assistant"/"system", "content": "..."}`. Anthropic handles `system` separately as a top-level parameter
- **Thread-local SQLite:** `app/history.py` uses `threading.local()` for per-thread DB connections (required by Gunicorn workers)
- **SMS commands:** `HELP` and `CLEAR` are handled before AI query in `sms.py`
- **SMS truncation:** Responses are capped at 1600 characters

## Configuration

All config is loaded via environment variables in `app/config.py`. Key settings:

| Variable | Default | Purpose |
|---|---|---|
| `AI_PROVIDER` | `openai` | Which AI backend: openai, anthropic, ollama |
| `OPENAI_API_KEY` | | OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model name |
| `ANTHROPIC_API_KEY` | | Anthropic API key |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-20250514` | Anthropic model name |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.2` | Ollama model name |
| `TWILIO_ACCOUNT_SID` | | Twilio Account SID |
| `TWILIO_AUTH_TOKEN` | | Twilio Auth Token (empty = skip validation) |
| `SYSTEM_PROMPT` | (concise SMS assistant) | AI system prompt |
| `MAX_HISTORY` | `10` | Conversation messages to include as context |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `5000` | Server port |

## Code Conventions

- **Naming:** snake_case for modules, functions, variables; UPPER_CASE for constants
- **Private functions:** Prefixed with underscore (`_validate_twilio_request`, `_build_messages`, `_get_conn`)
- **Dependencies:** Pinned to minor versions (`flask==3.1.*`) in requirements.txt
- **No test framework** is currently configured
- **No linter/formatter** is currently configured
- **Logging:** Python `logging` module, configured in `main.py`

## Sensitive Files

Never commit: `.env`, `*.db` (both in `.gitignore`)
