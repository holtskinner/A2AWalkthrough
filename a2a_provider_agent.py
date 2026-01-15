import asyncio
import os

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from langgraph_a2a_server import A2AServer

from helpers import setup_env
from provider_agent import ProviderAgent


def main() -> None:
    print("Running Healthcare Provider Agent")
    setup_env()

    HOST = os.environ.get("AGENT_HOST", "localhost")
    PORT = int(os.environ.get("PROVIDER_AGENT_PORT"))

    agent = asyncio.run(ProviderAgent().initialize())

    agent_card = AgentCard(
        name="HealthcareProviderAgent",
        description="An agent that can find and list healthcare providers based on a user's location and desired specialty.",
        url=f"http://{HOST}:{PORT}/",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=False),
        skills=[
            AgentSkill(
                id="find_healthcare_providers",
                name="Find Healthcare Providers",
                description="Finds and lists healthcare providers based on user's location and specialty.",
                tags=["healthcare", "providers", "doctor", "psychiatrist"],
                examples=[
                    "Are there any Psychiatrists near me in Boston, MA?",
                    "Find a pediatrician in Springfield, IL.",
                ],
            )
        ],
    )

    server = A2AServer(
        graph=agent.agent,
        agent_card=agent_card,
        host=HOST,
        port=PORT,
    )

    server.serve(app_type="starlette")


if __name__ == "__main__":
    main()
