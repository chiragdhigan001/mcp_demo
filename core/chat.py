from core.claude import Claude
from mcp_client import MCPClient
from core.tools import ToolManager


class Chat:

    def __init__(
        self,
        claude_service: Claude,
        clients: dict[str, MCPClient]
    ):

        self.claude_service = claude_service
        self.clients = clients

        self.messages = []

    async def _process_query(self, query: str):

        self.messages.append({
            "role": "user",
            "content": query
        })

    async def run(
        self,
        query: str,
    ) -> str:

        # IMPORTANT:
        # This allows CliChat to override _process_query()
        await self._process_query(query)

        response = self.claude_service.chat(
            messages=self.messages,
            tools=await ToolManager.get_all_tools(self.clients),
        )

        self.messages.append({
            "role": "assistant",
            "content": response
        })

        return response