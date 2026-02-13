# Blah Blah Answers

SMS-to-AI gateway for dumb phones. Text a question, get an answer — no data plan needed.

Supports OpenAI, Anthropic, Google Gemini, and Ollama (fully local) as AI backends. Completely self-hostable.

## How It Works

1. User sends an SMS to your Twilio phone number
2. Twilio forwards the message to this server via webhook
3. The server queries your configured AI provider
4. The AI response is sent back as an SMS

## Quick Start

### Prerequisites

- A [Twilio](https://www.twilio.com/) account with an SMS-capable phone number
- An API key for your chosen AI provider (or Ollama installed locally)
- Python 3.10+ or Docker

### Setup

1. Clone the repo and configure your environment:

```bash
git clone https://github.com/parkerspitzer/blah-blah-answers.git
cd blah-blah-answers
cp .env.example .env
```

2. Edit `.env` with your API keys and preferred AI provider.

3. Run with Docker (recommended):

```bash
docker compose up -d
```

Or run directly with Python:

```bash
pip install -r requirements.txt
python -m app.main
```

4. Configure your Twilio phone number's webhook:
   - Go to your [Twilio Console](https://console.twilio.com/) > Phone Numbers > Your Number
   - Under "Messaging", set "A message comes in" to your server's URL: `https://your-server.com/sms`
   - Method: `HTTP POST`

### Exposing Your Server

If running locally, you need a public URL for Twilio to reach your server. Options:

- **ngrok**: `ngrok http 5000` — gives you a public URL for development
- **Reverse proxy**: Use nginx/caddy with a domain and SSL for production
- **VPS**: Deploy to any cloud provider and point your domain at it

## Configuration

All configuration is done through environment variables (`.env` file). See `.env.example` for all options.

| Variable | Description | Default |
|---|---|---|
| `AI_PROVIDER` | `openai`, `anthropic`, `gemini`, or `ollama` | `openai` |
| `OPENAI_API_KEY` | Your OpenAI API key | |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4o-mini` |
| `ANTHROPIC_API_KEY` | Your Anthropic API key | |
| `ANTHROPIC_MODEL` | Anthropic model to use | `claude-sonnet-4-20250514` |
| `GEMINI_API_KEY` | Your Google Gemini API key | |
| `GEMINI_MODEL` | Gemini model to use | `gemini-2.5-flash` |
| `OLLAMA_URL` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Ollama model to use | `llama3.2` |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID | |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token (for request validation) | |
| `SYSTEM_PROMPT` | System prompt for normal responses (160 chars) | (see .env.example) |
| `CONTEXT_PROMPT` | System prompt for `/context` responses (480 chars) | (see .env.example) |
| `CONTEXT_TIMEOUT_MINUTES` | Minutes of inactivity before auto-clearing conversation | `30` |
| `MAX_HISTORY` | Messages of context to keep per number | `10` |

## Using Ollama (Fully Local)

For a completely local setup with no external API calls:

1. [Install Ollama](https://ollama.com/)
2. Pull a model: `ollama pull llama3.2`
3. Set in your `.env`:
   ```
   AI_PROVIDER=ollama
   OLLAMA_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2
   ```

Or uncomment the Ollama service in `docker-compose.yml` to run it alongside the app.

## SMS Commands

Users can text these commands to your number:

| Command | Description |
|---|---|
| `HELP` | Show available commands |
| `CLEAR` or `/CLEAR` | Erase conversation history |
| `/CONTEXT` | Get a detailed, longer answer to your last question (up to 480 characters / 3 SMS segments) |

Any other text is treated as a question for the AI. Normal responses are kept concise at 160 characters (1 SMS segment).

### Auto-Expiry

Conversations automatically clear after 30 minutes of inactivity (configurable via `CONTEXT_TIMEOUT_MINUTES`). This keeps responses relevant without requiring users to manually clear history.

## Endpoints

- `POST /sms` — Twilio webhook for incoming SMS
- `GET /health` — Health check (returns provider info)

## License

GPL-3.0 — see [LICENSE](LICENSE) for details.
