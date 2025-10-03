import asyncio
import base64
import os

import google.auth
import google.auth.transport.requests
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
from agent_framework import ChatAgent, MCPStdioTool
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv
from google.auth import default


class ProviderAgentExecutor(AgentExecutor):
    """Example using a local MCP server via stdio."""

    def __init__(self) -> None:
        load_dotenv()

        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        location = "global"
        base_url = f"https://aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/endpoints/openapi"

        # Get Google Cloud Credentials
        credentials, _ = default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        credentials.refresh(google.auth.transport.requests.Request())

        self.mcp_server = MCPStdioTool(
            name="healthcare_providers",
            command="uv",
            args=["run", "mcpserver.py"],
        )
        self.agent = ChatAgent(
            chat_client=OpenAIChatClient(
                model_id="openai/gpt-oss-120b-maas",
                base_url=base_url,
                api_key=credentials.token,
            ),
            name="HealthcareProviderAgent",
            instructions="Your task is to find and list providers using the healthcare_providers MCP Tool based on the users query.",
        )

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        result = await self.agent.run(
            context.get_user_input(),
            tools=self.mcp_server,
        )

        # Use only the response after the tool call
        await event_queue.enqueue_event(
            new_agent_text_message(result.messages[-1].text)
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass


if __name__ == "__main__":
    HOST = "localhost"
    PORT = 8001

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
        name="Healthcare Provider Finder Agent",
        description="An agent that can find and list healthcare providers based on a user's location (state) and desired specialty.",
        url=f"http://{HOST}:{PORT}/",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
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
