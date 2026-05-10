from typing import List
from mcp.types import Prompt, PromptMessage  # type: ignore[import]

from core.chat import Chat
from core.claude import Claude
from mcp_client import MCPClient

MessageParam = dict


class CliChat(Chat):

    def __init__(
        self,
        doc_client: MCPClient,
        clients: dict[str, MCPClient],
        claude_service: Claude,
    ):

        super().__init__(
            clients=clients,
            claude_service=claude_service
        )

        self.doc_client = doc_client

    async def list_prompts(self) -> list[Prompt]:

        return await self.doc_client.list_prompts()

    async def list_docs_ids(self) -> list[str]:

        result = await self.doc_client.read_resource(
            "docs://documents"
        )

        if isinstance(result, list):
            return result

        if isinstance(result, str):

            try:
                import json
                return json.loads(result)

            except Exception:
                return []

        return []

    async def get_doc_content(self, doc_id: str) -> str:

        result = await self.doc_client.read_resource(
            f"docs://documents/{doc_id}"
        )

        return str(result)

    async def get_prompt(
        self,
        command: str,
        doc_id: str
    ) -> list[PromptMessage]:

        return await self.doc_client.get_prompt(
            command,
            {"doc_id": doc_id}
        )

    async def _extract_resources(
        self,
        query: str
    ) -> str:

        query_lower = query.lower()

        doc_ids = await self.list_docs_ids()

        mentioned_docs = []

        for doc_id in doc_ids:

            if (
                f"@{doc_id.lower()}" in query_lower
                or doc_id.lower() in query_lower
            ):

                content = await self.get_doc_content(doc_id)

                mentioned_docs.append(
                    f"""
Document: {doc_id}

Content:
{content}
"""
                )

        return "\n".join(mentioned_docs)

    async def _process_command(
        self,
        query: str
    ) -> bool:

        if not query.startswith("/"):
            return False

        words = query.split()

        if len(words) < 2:
            return False

        command = words[0].replace("/", "")
        doc_id = words[1]

        messages = await self.doc_client.get_prompt(
            command,
            {"doc_id": doc_id}
        )

        self.messages += convert_prompt_messages_to_message_params(
            messages
        )

        return True

    async def _process_query(self, query: str):

        if await self._process_command(query):
            return

        added_resources = await self._extract_resources(query)

        prompt = f"""
You are a helpful AI assistant.

User question:
{query}

Relevant document context:
{added_resources}

Instructions:
- Use the provided document context if relevant.
- Answer clearly and directly.
- If document content exists, summarize or explain it.
- Do not say content is unavailable unless no context exists.
"""

        self.messages.append({
            "role": "user",
            "content": prompt
        })


def convert_prompt_message_to_message_param(
    prompt_message: PromptMessage,
) -> MessageParam:

    role = (
        "user"
        if prompt_message.role == "user"
        else "assistant"
    )

    content = prompt_message.content

    if isinstance(content, str):

        return {
            "role": role,
            "content": content
        }

    if isinstance(content, list):

        text = ""

        for item in content:

            if isinstance(item, dict):

                if item.get("type") == "text":
                    text += item.get("text", "") + "\n"

            elif hasattr(item, "text"):
                text += getattr(item, "text", "") + "\n"

        return {
            "role": role,
            "content": text
        }

    return {
        "role": role,
        "content": str(content)
    }


def convert_prompt_messages_to_message_params(
    prompt_messages: List[PromptMessage],
) -> List[MessageParam]:

    return [
        convert_prompt_message_to_message_param(msg)
        for msg in prompt_messages
    ]