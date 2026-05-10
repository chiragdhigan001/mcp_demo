import sys
import asyncio
import json
from typing import Optional, Any
from contextlib import AsyncExitStack
from pydantic import AnyUrl
from mcp import (
    ClientSession,
    StdioServerParameters,
    types,
)

from mcp.client.stdio import stdio_client


class MCPClient:

    def __init__(
        self,
        command: str,
        args: list[str],
        env: Optional[dict] = None,
    ):

        self._command = command
        self._args = args
        self._env = env

        self._session: Optional[ClientSession] = None

        self._exit_stack: AsyncExitStack = AsyncExitStack()

    async def connect(self):

        server_params = StdioServerParameters(
            command=self._command,
            args=self._args,
            env=self._env,
        )

        stdio_transport = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )

        _stdio, _write = stdio_transport

        self._session = await self._exit_stack.enter_async_context(
            ClientSession(_stdio, _write)
        )

        await self._session.initialize()

    def session(self) -> ClientSession:

        if self._session is None:

            raise ConnectionError(
                "Client session not initialized."
            )

        return self._session

    async def list_tools(self) -> list[types.Tool]:

        result = await self.session().list_tools()

        return result.tools

    async def call_tool(
        self,
        tool_name: str,
        tool_input: dict
    ) -> types.CallToolResult | None:

        return await self.session().call_tool(
            tool_name,
            tool_input
        )

    async def list_prompts(self) -> list[types.Prompt]:

        result = await self.session().list_prompts()

        return result.prompts

    async def get_prompt(
        self,
        prompt_name,
        args: dict[str, str]
    ):

        result = await self.session().get_prompt(
            prompt_name,
            args
        )

        return result.messages

    async def read_resource(
        self,
        resource_uri: str
    ) -> Any:

        result = await self.session().read_resource(
            resource_uri
        )

        if hasattr(result, "contents"):

            contents = result.contents

            if contents and len(contents) > 0:

                first = contents[0]

                if hasattr(first, "text"):
                    return first.text

                return str(first)

        return ""

    async def cleanup(self):

        await self._exit_stack.aclose()

        self._session = None

    async def __aenter__(self):

        await self.connect()

        return self

    async def __aexit__(
        self,
        exc_type,
        exc_val,
        exc_tb
    ):

        await self.cleanup()


# Testing
async def main():

    async with MCPClient(
        command="uv",
        args=["run", "mcp_server.py"],
    ) as client:

        docs = await client.read_resource(
            "docs://documents"
        )

        print(docs)

        report = await client.read_resource(
            "docs://documents/report.pdf"
        )

        print(report)


if __name__ == "__main__":

    asyncio.run(main())