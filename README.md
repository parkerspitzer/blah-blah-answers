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
- **Docker** (recommended) or **Python 3.10+**

### Step 1: Clone the Repository

```bash
git clone https://github.com/parkerspitzer/blah-blah-answers.git
cd blah-blah-answers
```

### Step 2: Configure Environment Variables

Copy the example configuration file and open it in your editor:

```bash
cp .env.example .env
```

At minimum, you need to fill in:

- **`AI_PROVIDER`** — choose one of: `openai`, `anthropic`, `gemini`, or `ollama`
- **The API key** for your chosen provider (e.g. `OPENAI_API_KEY`)
- **`TWILIO_ACCOUNT_SID`** and **`TWILIO_AUTH_TOKEN`** — find these in your [Twilio Console](https://console.twilio.com/) dashboard

If you leave `TWILIO_AUTH_TOKEN` empty, Twilio request validation is skipped (useful for local testing, but not recommended for production).

### Step 3: Run the Server

#### Option A: Docker (recommended)

```bash
docker compose up -d
```

This builds the image and starts the server on port 5000. Conversation history is persisted in a `data/` directory on the host.

To view logs:

```bash
docker compose logs -f
```

To stop:

```bash
docker compose down
```

To rebuild after code changes:

```bash
docker compose up -d --build
```

#### Option B: Run Directly with Python

```bash
pip install -r requirements.txt
python -m app.main
```

The server starts on `http://0.0.0.0:5000` by default (configurable via `HOST` and `PORT` in `.env`).

### Step 4: Configure Twilio Webhook

1. Go to your [Twilio Console](https://console.twilio.com/)
2. Navigate to **Phone Numbers** > **Manage** > **Active Numbers**
3. Click on your SMS-capable phone number
4. Under **Messaging** > **"A message comes in"**, set:
   - **URL**: `https://your-server.com/sms`
   - **Method**: `HTTP POST`
5. Click **Save**

### Step 5: Expose Your Server

Twilio needs a public URL to reach your server. Choose one of these approaches:

**For development/testing:**

- **ngrok** (free): Run `ngrok http 5000`, then copy the `https://...` URL it gives you into your Twilio webhook configuration. The URL changes each time you restart ngrok.

**For production:**

- **VPS** (e.g. DigitalOcean, Linode, AWS): Deploy the Docker container on a server and point a domain at it.
- **Reverse proxy**: Put nginx or Caddy in front of the app to handle SSL. Example with Caddy:
  ```
  your-domain.com {
      reverse_proxy localhost:5000
  }
  ```

### Step 6: Test It

Send an SMS to your Twilio number. You should get an AI-generated response back within a few seconds. You can also check the health endpoint:

```bash
curl http://localhost:5000/health
# Returns: {"status": "ok", "provider": "openai"}
```

## Configuration

All configuration is done through environment variables in the `.env` file. See `.env.example` for all options with descriptions.

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
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token (empty = skip validation) | |
| `SYSTEM_PROMPT` | System prompt for normal responses (160 chars) | (see .env.example) |
| `CONTEXT_PROMPT` | System prompt for `/context` responses (480 chars) | (see .env.example) |
| `CONTEXT_TIMEOUT_MINUTES` | Minutes of inactivity before auto-clearing conversation | `30` |
| `MAX_HISTORY` | Messages of context to keep per number | `10` |
| `HOST` | Server bind address | `0.0.0.0` |
| `PORT` | Server port | `5000` |

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

### Running Ollama with Docker Compose

You can also run Ollama as a Docker container alongside the app. Uncomment the `ollama` service in `docker-compose.yml`, then **update your `.env`** to use Docker's internal networking:

```
AI_PROVIDER=ollama
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2
```

Note: You must use `http://ollama:11434` (the Docker service name), **not** `http://localhost:11434`, because the containers communicate over Docker's internal network.

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

## Data Storage

Conversation history is stored in a SQLite database at `data/conversations.db`. This file is created automatically on first run.

- **Docker**: The `data/` directory is mounted as a volume, so conversations persist across container restarts.
- **Direct Python**: The `data/` directory is created automatically in the project root.

The database and `data/` directory are excluded from version control via `.gitignore`.

## Endpoints

- `POST /sms` — Twilio webhook for incoming SMS
- `GET /health` — Health check (returns provider info)

## Troubleshooting

- **No response to SMS**: Check that your Twilio webhook URL is correct and publicly accessible. Check the server logs (`docker compose logs -f`).
- **"Invalid Twilio request" errors**: Make sure `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` in your `.env` match the values in your Twilio Console. For local testing, you can leave `TWILIO_AUTH_TOKEN` empty to skip validation.
- **Ollama not connecting in Docker**: Use `OLLAMA_URL=http://ollama:11434` (not `localhost`) when running Ollama as a Docker Compose service.
- **Port conflicts**: Change `PORT` in your `.env` to use a different host port.

## License

GPL-3.0 — see [LICENSE](LICENSE) for details.
