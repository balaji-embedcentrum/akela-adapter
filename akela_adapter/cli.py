"""CLI entry point for akela-adapter."""
import argparse
import asyncio
import os
from .adapter import AkelaAdapter, DEFAULT_AKELA_API_URL


def main():
    parser = argparse.ArgumentParser(
        prog="akela-adapter",
        description="Connect any OpenAI-compatible agent to an Akela pack",
        epilog="Example: AKELA_API_KEY=ak_live_xxx akela-adapter",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("AKELA_API_KEY", ""),
        help="Agent API key from akela-ai dashboard (or AKELA_API_KEY env) — required",
    )
    parser.add_argument(
        "--agent-url",
        default=os.getenv("AGENT_ENDPOINT_URL", "http://localhost:8642"),
        help="Local agent endpoint (default: http://localhost:8642)",
    )
    parser.add_argument(
        "--agent-key",
        default=os.getenv("AGENT_ENDPOINT_KEY", ""),
        help="Bearer token for agent endpoint if needed",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("LLM_MODEL", "default"),
        help="Model name to pass to agent",
    )
    # Self-hosting override — not needed for akela-ai SaaS users
    parser.add_argument(
        "--api-url",
        default=os.getenv("AKELA_API_URL", DEFAULT_AKELA_API_URL),
        help=f"Akela API base URL (default: {DEFAULT_AKELA_API_URL}). Override only if self-hosting.",
    )

    args = parser.parse_args()

    if not args.api_key:
        parser.error(
            "API key is required.\n"
            "  Set it with: export AKELA_API_KEY=ak_live_xxxx\n"
            "  Get your key from the akela-ai dashboard → agent settings."
        )

    adapter = AkelaAdapter(
        api_key=args.api_key,
        api_url=args.api_url,
        agent_endpoint=args.agent_url,
        model=args.model,
        agent_endpoint_key=args.agent_key,
    )

    try:
        asyncio.run(adapter.run())
    except KeyboardInterrupt:
        print("\n[akela-adapter] Stopped.")


if __name__ == "__main__":
    main()
