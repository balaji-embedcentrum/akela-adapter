"""CLI entry point for akela-adapter."""
import argparse
import asyncio
import os
from .adapter import AkelaAdapter


def main():
    parser = argparse.ArgumentParser(
        prog="akela-adapter",
        description="Connect any OpenAI-compatible agent to an Akela pack",
        epilog="Example: akela-adapter --api-url http://akela.example.com:8200 --api-key akela_xxx --name my-agent",
    )
    parser.add_argument("--api-url", default=os.getenv("AKELA_API_URL", ""), help="Akela API base URL (or AKELA_API_URL env)")
    parser.add_argument("--api-key", default=os.getenv("AKELA_API_KEY", ""), help="Agent API key from Akela registration (or AKELA_API_KEY env)")
    parser.add_argument("--agent-url", default=os.getenv("AGENT_ENDPOINT_URL", "http://localhost:8642"), help="Local agent endpoint (default: http://localhost:8642)")
    parser.add_argument("--agent-key", default=os.getenv("AGENT_ENDPOINT_KEY", ""), help="Bearer token for agent endpoint if needed")
    parser.add_argument("--name", default=os.getenv("AGENT_NAME", "external-agent"), help="Agent name as registered in Akela")
    parser.add_argument("--model", default=os.getenv("LLM_MODEL", "default"), help="Model name to pass to agent")

    args = parser.parse_args()

    if not args.api_url:
        parser.error("--api-url is required (or set AKELA_API_URL)")
    if not args.api_key:
        parser.error("--api-key is required (or set AKELA_API_KEY)")

    adapter = AkelaAdapter(
        api_url=args.api_url,
        api_key=args.api_key,
        agent_endpoint=args.agent_url,
        agent_name=args.name,
        model=args.model,
        agent_endpoint_key=args.agent_key,
    )

    try:
        asyncio.run(adapter.run())
    except KeyboardInterrupt:
        print("\n[akela-adapter] Stopped.")


if __name__ == "__main__":
    main()
