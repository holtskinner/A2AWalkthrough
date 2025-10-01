import asyncio
import logging
from typing import Any
from uuid import uuid4

import httpx
from a2a.client.transports.jsonrpc import JsonRpcTransport
from a2a.types import (
    Message,
    MessageSendParams,
    Part,
    Role,
    SendMessageRequest,
    TextPart,
)


async def main() -> None:
    base_url = "http://0.0.0.0:9999"

    prompt = "How much would I pay for mental health therapy?"
    async with httpx.AsyncClient() as httpx_client:
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
        print(response.model_dump(mode="json", exclude_none=True))


if __name__ == "__main__":
    asyncio.run(main())
