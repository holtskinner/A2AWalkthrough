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


async def send_message(client: JsonRpcTransport, prompt: str) -> str:
    response: Message = await client.send_message(
        MessageSendParams(
            message=Message(
                message_id=uuid4().hex,
                role=Role.user,
                parts=[Part(TextPart(text=prompt))],
            )
        )
    )

    console.print(f"[blue]Message ID:[/] {response.message_id}")
    return response.parts[0].root.text


async def run_hospital_workflow() -> None:
    prompt = "How can I get mental health therapy?"

    async with httpx.AsyncClient(timeout=100.0) as httpx_client:
        policy_client = JsonRpcTransport(
            httpx_client=httpx_client,
            url="http://0.0.0.0:9999",
        )
        health_client = JsonRpcTransport(
            httpx_client=httpx_client,
            url="http://0.0.0.0:9998",
        )

        response1 = await send_message(health_client, prompt)
        console.print("[magenta]Health Agent Response:[/]")
        console.print(Markdown(response1))

        response2 = await send_message(
            policy_client,
            f"Context: {response1} Give information about the coverage for this treatment.",
        )
        console.print("[yellow]Policy Agent Response:[/]")
        console.print(Markdown(response2))


if __name__ == "__main__":

    console = Console()
    asyncio.run(run_hospital_workflow())
