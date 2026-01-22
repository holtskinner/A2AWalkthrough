import asyncio
import os

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from langchain.agents import create_agent
from langchain_litellm import ChatLiteLLM
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import StdioConnection
from langgraph.graph.state import CompiledStateGraph
from langgraph_a2a_server import A2AServer

from helpers import setup_env


def main() -> None:
    print("Running Healthcare Provider Agent")
    setup_env()

    HOST = os.getenv("AGENT_HOST", "localhost")
    PORT = int(os.getenv("PROVIDER_AGENT_PORT"))

    mcp_client = MultiServerMCPClient(
        {
            "find_healthcare_providers": StdioConnection(
                transport="stdio",
                command="uv",
                args=["run", "mcpserver.py"],
            )
        }
    )
    agent: CompiledStateGraph = create_agent(
        model=ChatLiteLLM(
            model="gemini/gemini-3-flash-preview",
            # For Vertex AI:
            # model="vertex_ai/gemini-3-flash-preview",
            max_tokens=1000,
        ),
        tools=asyncio.run(mcp_client.get_tools()),
        name="HealthcareProviderAgent",
        system_prompt="Find and list healthcare providers using the find_healthcare_providers MCP Tool.",
    )

    agent_card = AgentCard(
        name="HealthcareProviderAgent",
        description="Find healthcare providers by location and specialty.",
        url=f"http://{HOST}:{PORT}/",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=False),
        skills=[
            AgentSkill(
                id="find_healthcare_providers",
                name="Find Healthcare Providers",
                description="Finds providers based on location/specialty.",
                tags=["healthcare", "providers", "doctor", "psychiatrist"],
                examples=[
                    "Are there any Psychiatrists near me in Boston, MA?",
                    "Find a pediatrician in Springfield, IL.",
                ],
            )
        ],
    )

    server = A2AServer(
        graph=agent,
        agent_card=agent_card,
        host=HOST,
        port=PORT,
    )

    server.serve(app_type="starlette")


if __name__ == "__main__":
    main()
