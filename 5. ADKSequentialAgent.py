# Import the implementation from the file
import asyncio
import warnings

from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.agents.remote_a2a_agent import (
    AGENT_CARD_WELL_KNOWN_PATH,
    RemoteA2aAgent,
)
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.agent_tool import AgentTool
from google.genai import types

warnings.filterwarnings("ignore")


async def call_agent_async(agent, query):
    APP_NAME = "health_app"
    USER_ID = "user_1"
    SESSION_ID = "session_001"  # Using a fixed ID for simplicity

    content = types.Content(role="user", parts=[types.Part(text=query)])

    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)

    events = runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=content
    )

    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)


async def run_hospital_workflow() -> None:
    prompt = "How can I get mental health therapy?"

    policy_agent = RemoteA2aAgent(
        name="policy_agent",
        agent_card=f"http://0.0.0.0:9999{AGENT_CARD_WELL_KNOWN_PATH}",
    )
    health_research_agent = RemoteA2aAgent(
        name="health_agent",
        agent_card=f"http://0.0.0.0:9998{AGENT_CARD_WELL_KNOWN_PATH}",
    )

    root_agent = SequentialAgent(
        name="root_agent",
        description="Healthcare Routing Agent",
        sub_agents=[
            health_research_agent,
            policy_agent,
        ],
    )
    await call_agent_async(
        root_agent,
        prompt,
    )


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(run_hospital_workflow())
