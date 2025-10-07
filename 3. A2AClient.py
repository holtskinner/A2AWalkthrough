import asyncio
from uuid import uuid4

import httpx
from a2a.client.transports.jsonrpc import JsonRpcTransport
from a2a.types import (
    Message,
    MessageSendParams,
    Part,
    Role,
    TaskQueryParams,
    TextPart,
)
from rich.console import Console
from rich.markdown import Markdown


async def poll_task(client: JsonRpcTransport, task_id: str) -> str | None:
    """Polls a task status iteratively until it reaches a terminal state."""
    while True:
        task = await client.get_task(request=TaskQueryParams(id=task_id))
        state = task.status.state

        if state in {"completed", "failed", "cancelled"}:
            if state == "completed":
                if task.history:
                    last_message = task.history[-1]
                    if last_message.role == "agent" and last_message.parts:
                        return last_message.parts[0].root.text
            elif state == "failed":
                print("Task failed")
            elif state == "cancelled":
                print("Task cancelled")

            return None

        await asyncio.sleep(1)


async def main() -> None:
    base_url = "http://localhost:9999"

    prompt = "How much would I pay for mental health therapy?"

    console = Console()

    async with httpx.AsyncClient(timeout=100.0) as httpx_client:
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

        response = await client.send_message(request)

        if response.kind == "message":
            message_id = response.message_id
            text_content = response.parts[0].root.text

            console.print(f"[yellow]Message ID:[/] {message_id}")
        elif response.kind == "artifact":
            artifact_id = response.artifacts[0].artifact_id
            text_content = response.artifacts[0].parts[0].root.text

            console.print(f"[yellow]Artifact ID:[/] {artifact_id}")
        elif response.kind == "task":
            text_content = await poll_task(client, response.id)

        console.print(Markdown(text_content))


if __name__ == "__main__":
    asyncio.run(main())
