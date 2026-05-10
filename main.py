import asyncio
import sys
import os
from dotenv import load_dotenv  # type: ignore[import]
from contextlib import AsyncExitStack

from mcp_client import MCPClient
from core.claude import Claude

from core.cli_chat import CliChat
from core.cli import CliApp

load_dotenv()

# GROQ Config
model = os.getenv(
    "GROQ_MODEL",
    "llama3-70b-8192"
)

groq_api_key = os.getenv("GROQ_API_KEY", "")

assert groq_api_key, (
    "Error: GROQ_API_KEY cannot be empty. Update .env"
)


async def main():
    claude_service = Claude(model=model)

    server_scripts = sys.argv[1:]
    clients = {}

    command, args = (
        ("uv", ["run", "mcp_server.py"])
        if os.getenv("USE_UV", "0") == "1"
        else ("python", ["mcp_server.py"])
    )

    async with AsyncExitStack() as stack:

        # Main document MCP server
        doc_client = await stack.enter_async_context(
            MCPClient(command=command, args=args)
        )

        clients["doc_client"] = doc_client

        # Additional MCP servers
        for i, server_script in enumerate(server_scripts):
            client_id = f"client_{i}_{server_script}"

            client = await stack.enter_async_context(
                MCPClient(
                    command="uv",
                    args=["run", server_script]
                )
            )

            clients[client_id] = client

        # Chat system
        chat = CliChat(
            doc_client=doc_client,
            clients=clients,
            claude_service=claude_service,
        )

        # CLI App
        cli = CliApp(chat)

        await cli.initialize()
        await cli.run()


if __name__ == "__main__":
    asyncio.run(main())