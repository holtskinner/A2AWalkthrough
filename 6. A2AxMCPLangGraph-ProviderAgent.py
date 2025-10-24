import asyncio
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
from dotenv import load_dotenv
from google.auth import default
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import StdioConnection
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from helpers import authenticate


class ProviderAgentExecutor(AgentExecutor):
    """Example using a local MCP server via stdio."""

    def __init__(self) -> None:
        credentials, project_id = authenticate()
        location = "us-central1"
        base_url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/endpoints/openapi"

        mcp_client = MultiServerMCPClient(
            {
                "find_healthcare_providers": StdioConnection(
                    transport="stdio",
                    command="uv",
                    args=["run", "mcpserver.py"],
                )
            }
        )
        tools = asyncio.run(mcp_client.get_tools())
        self.agent = create_react_agent(
            ChatOpenAI(
                model="openai/gpt-oss-20b-maas",
                openai_api_key=credentials.token,
                openai_api_base=base_url,
            ),
            tools,
            name="HealthcareProviderAgent",
            prompt="Your task is to find and list providers using the find_healthcare_providers MCP Tool based on the users query. Only use providers based on the response from the tool.",
        )

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        print(context)
        prompt = context.get_user_input()
        print(prompt)

        response = await self.agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ]
            }
        )
        # Use only the response after the tool call
        await event_queue.enqueue_event(
            new_agent_text_message(response["messages"][-1].content)
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass


if __name__ == "__main__":
    print("Running Healthcare Provider Agent")
    load_dotenv()
    HOST = os.environ.get("AGENT_HOST")
    PORT = int(os.environ.get("PROVIDER_AGENT_PORT"))

    agent_executor = ProviderAgentExecutor()
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
        name=agent_executor.agent.name,
        description="An agent that can find and list healthcare providers based on a user's location and desired specialty.",
        url=f"http://{HOST}:{PORT}/",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor,
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    uvicorn.run(server.build(), host=HOST, port=PORT)
