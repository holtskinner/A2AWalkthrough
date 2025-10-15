# Import the implementation from the file
import asyncio
import os
import warnings

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import (
    AGENT_CARD_WELL_KNOWN_PATH,
    RemoteA2aAgent,
)
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.agent_tool import AgentTool
from google.genai import types

warnings.filterwarnings("ignore")


async def call_agent_async(agent, query) -> None:
    APP_NAME = "health_app"
    USER_ID = "user_1"
    SESSION_ID = "session_001"  # Using a fixed ID for simplicity

    content = types.Content(role="user", parts=[types.Part(text=query)])

    session_service = InMemorySessionService()
    await session_service.create_session(
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
    load_dotenv()
    host = os.environ.get("AGENT_HOST", "localhost")
    policy_port = os.environ.get("POLICY_AGENT_PORT", 9999)
    research_port = os.environ.get("RESEARCH_AGENT_PORT", 9998)
    provider_port = os.environ.get("PROVIDER_AGENT_PORT", 8001)

    policy_agent = RemoteA2aAgent(
        name="policy_agent",
        agent_card=f"http://{host}:{policy_port}{AGENT_CARD_WELL_KNOWN_PATH}",
    )
    health_agent = RemoteA2aAgent(
        name="health_agent",
        agent_card=f"http://{host}:{research_port}{AGENT_CARD_WELL_KNOWN_PATH}",
    )
    providers_agent = RemoteA2aAgent(
        name="providers_agent",
        agent_card=f"http://{host}:{provider_port}{AGENT_CARD_WELL_KNOWN_PATH}",
    )

    root_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="root_agent",
        description="Healthcare Routing Agent",
        instruction="""
        You are an agent for healthcare services. Your task is to call on one or more agent tools to answer questions and provide a detailed summary of their answers. Use `health_agent` for general healthcare questions, `providers_agent` for finding providers in their State, and `policy_agent` for questions on Health Insurance Policies. In your output, put which agent gave you the information.
        """,
        tools=[
            AgentTool(
                agent=health_agent,
            ),
            AgentTool(
                agent=policy_agent,
            ),
            AgentTool(
                agent=providers_agent,
            ),
        ],
    )

    await call_agent_async(
        root_agent,
        "I'm based in Boston, MA. How do I get mental health therapy near me and what does my insurance cover?",
    )


if __name__ == "__main__":
    asyncio.run(run_hospital_workflow())
