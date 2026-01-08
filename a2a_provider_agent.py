import os

import uvicorn
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from a2a.utils import new_agent_text_message
from dotenv import load_dotenv

from provider_agent import ProviderAgent


class ProviderAgentExecutor(AgentExecutor):
    """This is an agent for finding healthcare providers based on location and specialty."""

    def __init__(self) -> None:
        # Don't await in __init__ - it's not async
        self.agent = None

    async def _ensure_initialized(self) -> None:
        """Lazy initialization of the agent."""
        if self.agent is None:
            self.agent = await ProviderAgent().initialize()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        await self._ensure_initialized()

        prompt = context.get_user_input()
        response = await self.agent.answer_query(prompt)
        await event_queue.enqueue_event(new_agent_text_message(response))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass


def main():
    print("Running Healthcare Provider Agent")
    load_dotenv()

    HOST = os.environ.get("AGENT_HOST", "localhost")
    PORT = int(os.environ.get("PROVIDER_AGENT_PORT", 9997))

    skill = AgentSkill(
        id="find_healthcare_providers",
        name="Find Healthcare Providers",
        description="Finds and lists healthcare providers based on user's location and specialty.",
        tags=["healthcare", "providers", "doctor", "psychiatrist"],
        examples=[
            "Are there any Psychiatrists near me in Boston, MA?",
            "Find a pediatrician in Springfield, IL.",
        ],
    )

    agent_card = AgentCard(
        name="HealthcareProviderAgent",
        description="An agent that can find and list healthcare providers based on a user's location and desired specialty.",
        url=f"http://{HOST}:{PORT}/",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=False),
        skills=[skill],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=ProviderAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    uvicorn.run(server.build(), host=HOST, port=PORT)


if __name__ == "__main__":
    main()
