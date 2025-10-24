import asyncio
import os
import warnings

from dotenv import load_dotenv
from google.adk.agents import BaseAgent, SequentialAgent
from google.adk.agents.remote_a2a_agent import (
    RemoteA2aAgent,
)
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from rich.console import Console
from rich.markdown import Markdown

warnings.filterwarnings("ignore")


async def call_agent_async(agent: BaseAgent, query: str) -> None:
    print("Running Healthcare Workflow Agent")
    console = Console()
    APP_NAME = "health_app"
    USER_ID = "user_1"
    SESSION_ID = "session_001"  # Using a fixed ID for simplicity

    content = types.Content(role="user", parts=[types.Part(text=query)])

    session_service = InMemorySessionService()
    _ = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)

    events = runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=content
    )

    async for event in events:
        if event.is_final_response():
            text_content = event.content.parts[0].text
            console.print(Markdown(text_content))


async def run_hospital_workflow() -> None:
    load_dotenv()

    host = os.environ.get("AGENT_HOST")
    policy_port = os.environ.get("POLICY_AGENT_PORT")
    research_port = os.environ.get("RESEARCH_AGENT_PORT")

    prompt = "How can I get mental health therapy?"

    policy_agent = RemoteA2aAgent(
        name="policy_agent",
        agent_card=f"http://{host}:{policy_port}",
    )
    print("\tℹ️", f"{policy_agent.name} initialized")
    health_research_agent = RemoteA2aAgent(
        name="health_research_agent",
        agent_card=f"http://{host}:{research_port}",
    )
    print("\tℹ️", f"{health_research_agent.name} initialized")

    root_agent = SequentialAgent(
        name="root_agent",
        description="Healthcare Routing Agent",
        sub_agents=[
            health_research_agent,
            policy_agent,
        ],
    )
    print("\tℹ️", f"{root_agent.name} initialized")

    await call_agent_async(
        root_agent,
        prompt,
    )


if __name__ == "__main__":
    asyncio.run(run_hospital_workflow())
