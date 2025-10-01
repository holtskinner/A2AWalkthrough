import asyncio
from uuid import uuid4

import httpx
from a2a.client.transports.jsonrpc import JsonRpcTransport
from a2a.types import (
    Message,
    MessageSendParams,
    Part,
    Role,
    TextPart,
)
from rich.console import Console
from rich.markdown import Markdown


async def main() -> None:
    base_url = "http://0.0.0.0:9999"

    prompt = "How much would I pay for mental health therapy?"

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

        response: Message = await client.send_message(request)

        message_id = response.message_id
        text_content = response.parts[0].root.text

        console.print(f"[yellow]Message ID:[/] {message_id}")
        console.print(Markdown(text_content))


if __name__ == "__main__":
    asyncio.run(main())
