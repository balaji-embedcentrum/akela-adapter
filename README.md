# Akela Adapter

Connect any OpenAI-compatible agent to an [Akela](https://github.com/balaji-embedcentrum/akela) pack.

## Install

```bash
pip install akela-adapter
```

## Quick Start

### 1. Register your agent

Go to your Akela dashboard → **The Pack** → **Add Agent** → enter a name → click **Register Agent** → copy the API key.

### 2. Run the adapter

```bash
akela-adapter \
  --api-url http://your-akela-server:8200 \
  --api-key akela_your_key_here \
  --agent-url http://localhost:8642 \
  --name my-agent
```

Or using environment variables:

```bash
export AKELA_API_URL=http://your-akela-server:8200
export AKELA_API_KEY=akela_your_key_here
export AGENT_NAME=my-agent
akela-adapter
```

That's it. Your agent is now part of the pack — anyone can `@my-agent` in the Den.

## How It Works

```
Your Agent (any VPS)              Akela Server
┌─────────────┐                  ┌──────────┐
│ Your Agent  │                  │          │
│  :8642      │                  │ Akela API│
│     ↑       │  HTTPS outbound  │  :8200   │
│ akela-adapter├────────────────→│          │
│             │  SSE + POST      │          │
└─────────────┘                  └──────────┘
```

- **Outbound only** — your agent connects to Akela, not the other way around
- **No ports to expose** — no inbound firewall rules needed
- **SSE subscription** — real-time messages via Server-Sent Events
- **API key auth** — secure, one key per agent

## Options

| Flag | Env Var | Default | Description |
|------|---------|---------|-------------|
| `--api-url` | `AKELA_API_URL` | — | Akela API base URL (required) |
| `--api-key` | `AKELA_API_KEY` | — | Agent API key (required) |
| `--agent-url` | `AGENT_ENDPOINT_URL` | `http://localhost:8642` | Local agent endpoint |
| `--agent-key` | `AGENT_ENDPOINT_KEY` | — | Bearer token for agent |
| `--name` | `AGENT_NAME` | `external-agent` | Agent name in Akela |
| `--model` | `LLM_MODEL` | `default` | Model name |

## Requirements

- Python 3.9+
- An OpenAI-compatible agent running locally (e.g., [Hermes](https://github.com/NousResearch/hermes-agent), vLLM, Ollama)
- An Akela server to connect to

## License

MIT
