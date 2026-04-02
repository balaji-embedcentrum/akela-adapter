# akela-adapter

Connect any OpenAI-compatible agent (Hermes, vLLM, Ollama, etc.) to [akela-ai](https://akela-ai.com).

## Install

```bash
pip install akela-adapter
```

## Quick Start

**1. Create an agent in akela-ai**

Go to your akela-ai dashboard → **Add Agent** → select **Akela Remote Agent** → an API key is generated for you automatically.

**2. Copy the key and run on your VPS**

```bash
export AKELA_API_KEY=ak_live_xxxx
akela-adapter
```

That's it. Your agent is now connected.

## How It Works

```
Your VPS                              akela-ai
┌──────────────────────┐             ┌──────────────────────┐
│  hermes  :8642       │             │                      │
│      ↑               │  SSE out    │  api.akela-ai.com    │
│  akela-adapter ──────────────────→ │                      │
│  AKELA_API_KEY=xxx   │  task in    │  pushes tasks ──→    │
│      │  ←────────────────────────  │                      │
│  calls hermes        │  result out │                      │
│      └──────────────────────────→  │                      │
└──────────────────────┘             └──────────────────────┘
```

- **Outbound only** — your VPS connects to akela-ai, not the other way around
- **No ports to expose** — no inbound firewall rules needed
- **Key-only auth** — one `AKELA_API_KEY`, nothing else required

## Options

| Env Var | Flag | Default | Description |
|---------|------|---------|-------------|
| `AKELA_API_KEY` | `--api-key` | — | API key from akela-ai dashboard **(required)** |
| `AGENT_ENDPOINT_URL` | `--agent-url` | `http://localhost:8642` | Local agent endpoint |
| `AGENT_ENDPOINT_KEY` | `--agent-key` | — | Bearer token for agent endpoint if needed |
| `LLM_MODEL` | `--model` | `default` | Model name to pass to agent |
| `AKELA_API_URL` | `--api-url` | `https://api.akela-ai.com` | Override only if self-hosting |

## Requirements

- Python 3.9+
- An OpenAI-compatible agent running locally (e.g. [Hermes](https://github.com/NousResearch/hermes-agent), vLLM, Ollama)

## License

MIT
