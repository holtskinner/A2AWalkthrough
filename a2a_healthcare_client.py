import asyncio
import os
from typing import Any

from beeai_framework.adapters.a2a.agents import A2AAgent
from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.middleware.trajectory import EventMeta, GlobalTrajectoryMiddleware

from helpers import setup_env


class ConciseGlobalTrajectoryMiddleware(GlobalTrajectoryMiddleware):
    def _format_prefix(self, meta: EventMeta) -> str:
        prefix = super()._format_prefix(meta)
        return prefix.rstrip(": ")

    def _format_payload(self, value: Any) -> str:
        return ""


async def main() -> None:
    setup_env()

    host = os.getenv("AGENT_HOST")
    healthcare_agent_port = int(os.getenv("HEALTHCARE_AGENT_PORT"))

    agent = A2AAgent(
        url=f"http://{host}:{healthcare_agent_port}", memory=UnconstrainedMemory()
    )
    response = await agent.run(
        "I'm based in Austin, TX. How do I get mental health therapy near me and what does my insurance cover?"
    ).middleware(ConciseGlobalTrajectoryMiddleware())
    print(response.last_message.text)


if __name__ == "__main__":
    asyncio.run(main())
