"""
Akela Adapter — Standalone bridge for third-party agents.

Connects ANY OpenAI-compatible agent to an Akela pack.
The agent knows nothing about Akela — this adapter handles all communication.

Only needs:
  - AKELA_API_URL: The Akela API base URL
  - AKELA_API_KEY: Agent's API key (from Pack UI registration)
  - AGENT_ENDPOINT_URL: Local agent's OpenAI-compatible endpoint
  - AGENT_NAME: Agent's registered name in Akela
"""
import os
import json
import asyncio
import httpx


class AkelaAdapter:
    """Bridge between a local OpenAI-compatible agent and an Akela pack."""

    def __init__(
        self,
        api_url: str,
        api_key: str,
        agent_endpoint: str = "http://localhost:8642",
        agent_name: str = "external-agent",
        model: str = "default",
        agent_endpoint_key: str = "",
    ):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.agent_endpoint = agent_endpoint.rstrip("/")
        self.agent_name = agent_name
        self.model = model
        self.agent_endpoint_key = agent_endpoint_key
        self.agent_uuid = None
        self._stop_requested = False

    def _log(self, msg: str):
        print(f"[akela-adapter:{self.agent_name}] {msg}", flush=True)

    # ── Call the local agent ─────────────────────────────────────────
    async def call_agent(self, message: str) -> str:
        """Send a message to the local agent's OpenAI-compatible endpoint."""
        url = f"{self.agent_endpoint}/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": message}],
            "stream": False,
        }
        headers = {"Content-Type": "application/json"}
        if self.agent_endpoint_key:
            headers["Authorization"] = f"Bearer {self.agent_endpoint_key}"

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    return (
                        data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                    )
                else:
                    self._log(f"Agent returned {resp.status_code}: {resp.text[:200]}")
                    return f"[Agent error: {resp.status_code}]"
        except Exception as e:
            self._log(f"Failed to call agent: {e}")
            return f"[Agent unreachable: {e}]"

    # ── Post response to Akela ───────────────────────────────────────
    async def post_to_akela(self, room: str, content: str, mention_type: str = "direct"):
        """Post a message back to Akela as this agent."""
        url = f"{self.api_url}/chat/agent-message"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    url, json={"room": room, "content": content, "mention_type": mention_type}, headers=headers
                )
                if resp.status_code != 200:
                    self._log(f"Akela post failed {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            self._log(f"Akela post error: {e}")

    async def send_typing(self, room: str):
        """Send typing indicator to Akela."""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(f"{self.api_url}/chat/typing", json={"room": room}, headers=headers)
        except:
            pass

    # ── Handle incoming message ──────────────────────────────────────
    async def handle_message(self, data: dict):
        """Process an incoming message from Akela."""
        content = data.get("content", "")
        room = data.get("room", "general")
        sender = data.get("sender_name", "unknown")
        mention_type = data.get("mention_type", "direct")

        if not content.strip():
            return

        self._log(f"Message from {sender} in #{room}: {content[:80]}...")
        await self.send_typing(room)

        if self._stop_requested:
            self._log("Stop requested — skipping message")
            return

        response = await self.call_agent(content)

        if self._stop_requested:
            self._log("Stop requested — discarding response")
            return

        if response:
            await self.post_to_akela(room, response, mention_type)
            self._log(f"Responded in #{room}: {response[:80]}...")

    # ── SSE Listener ─────────────────────────────────────────────────
    async def listen(self):
        """Subscribe to Akela API via SSE and listen for messages."""
        subscribe_url = f"{self.api_url}/chat/subscribe/agent?token={self.api_key}"
        self._log("📡 Connecting to Akela...")

        while True:
            try:
                async with httpx.AsyncClient(timeout=None) as client:
                    async with client.stream("GET", subscribe_url) as response:
                        if response.status_code != 200:
                            self._log(f"SSE failed: {response.status_code}")
                            await asyncio.sleep(5)
                            continue

                        self._log("✅ Connected — listening for messages")

                        async for line in response.aiter_lines():
                            if not line or line.startswith(":"):
                                continue
                            if line.startswith("data: "):
                                try:
                                    data = json.loads(line[6:])
                                    if data.get("type") == "connected":
                                        self.agent_uuid = data.get("agent_id")
                                        self._log(f"🔗 Registered as {data.get('agent_name')} ({self.agent_uuid})")
                                        continue
                                    if data.get("type") == "stop":
                                        self._stop_requested = True
                                        self._log("🛑 Stop signal")
                                        continue
                                    if data.get("sender_name") == self.agent_name:
                                        continue
                                    self._stop_requested = False
                                    await self.handle_message(data)
                                except json.JSONDecodeError:
                                    pass
            except Exception as e:
                self._log(f"SSE error: {e} — reconnecting in 5s...")
            await asyncio.sleep(5)

    # ── Heartbeat ────────────────────────────────────────────────────
    async def heartbeat(self):
        """Periodic heartbeat so agent shows online in Akela."""
        await asyncio.sleep(5)
        while True:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    await client.put(f"{self.api_url}/agents/internal/heartbeat/{self.agent_name}")
                    self._log("♥ Heartbeat OK")
            except Exception as e:
                self._log(f"♥ Heartbeat error: {e}")
            await asyncio.sleep(20)

    # ── Run ──────────────────────────────────────────────────────────
    async def run(self):
        """Start the adapter — connects to Akela and listens for messages."""
        self._log("🐺 Akela Adapter v0.1.0")
        self._log(f"  Akela API:  {self.api_url}")
        self._log(f"  Agent:      {self.agent_endpoint}")
        self._log(f"  Name:       {self.agent_name}")

        # Wait for local agent to be ready
        endpoint = f"{self.agent_endpoint}/health"
        self._log(f"  Waiting for agent at {endpoint}...")
        for _ in range(60):
            try:
                async with httpx.AsyncClient(timeout=3.0) as client:
                    resp = await client.get(endpoint)
                    if resp.status_code == 200:
                        self._log("  ✅ Agent ready")
                        break
            except:
                pass
            await asyncio.sleep(1)

        await asyncio.gather(self.heartbeat(), self.listen())
