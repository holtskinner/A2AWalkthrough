import asyncio
from uuid import uuid4

import httpx
from a2a.client.transports.jsonrpc import JsonRpcTransport
from a2a.types import (
    Message,
    MessageSendParams,
    Part,
    Role,
    Task,
    TextPart,
)
from rich.console import Console
from rich.markdown import Markdown


async def main() -> None:
    base_url = "http://0.0.0.0:8001"

    prompt = "I'm based in Boston, MA. Are there any Psychiatrists near me?"

    console = Console()

    async with httpx.AsyncClient(timeout=10.0) as httpx_client:
        client = JsonRpcTransport(
            httpx_client=httpx_client,
            url=base_url,
        )

        request = MessageSendParams(
            message=Message(
                message_id=uuid4().hex,
                role=Role.user,
                parts=[Part(TextPart(text=prompt))],
            )
        )

        response: Task = await client.send_message(request)

        artifact = response.artifacts[0]
        artifact_id = artifact.artifact_id
        text_content = artifact.parts[0].root.text

        console.print(f"[yellow]Artifact ID:[/] {artifact_id}")
        console.print(Markdown(text_content))


if __name__ == "__main__":
    asyncio.run(main())
