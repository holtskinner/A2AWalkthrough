# Import the implementation from the file
import asyncio

from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import (
    AGENT_CARD_WELL_KNOWN_PATH,
    RemoteA2aAgent,
)
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types


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

    # policy_agent = RemoteA2aAgent(
    #     name="policy_agent",
    #     agent_card=f"http://0.0.0.0:9999{AGENT_CARD_WELL_KNOWN_PATH}",
    #     description="Provides information about insurance coverage options and details.",
    # )
    # health_agent = RemoteA2aAgent(
    #     name="health_agent",
    #     agent_card=f"http://0.0.0.0:9998{AGENT_CARD_WELL_KNOWN_PATH}",
    #     description="Provides information about symptoms, health conditions, treatments, and procedures using up-to-date web resources.",
    # )

    policy_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="policy_agent",
        description="Provides information about insurance coverage options and details.",
        instruction="""
        "You are an expert insurance agent designed to assist with coverage queries. Use the provided documents to answer questions about insurance policies. If the information is not available in the documents, respond with 'I don't know'"
        Here's the information about mental health coverage from the provided document:

        **Section:** If you need mental health, behavioral health, or substance abuse services

        **What You Will Pay:**

        *   **In-Network Provider (You will pay the least):**
            *   Office Visit: 10% coinsurance
            *   Other Outpatient: 10% coinsurance
            *   Inpatient services: 10% coinsurance
        *   **Out-of-Network Provider (You will pay the most):**
            *   Office Visit: 30% coinsurance
            *   Other Outpatient: 30% coinsurance
            *   Inpatient services: 30% coinsurance

        **Limitations, Exceptions, & Other Important Information:**

        *   **For Inpatient Physician Fees:**
            *   In-Network Providers: 10% coinsurance
            *   Out-of-Network Providers: 30% coinsurance
        """,
    )

    health_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="health_agent",
        tools=[google_search],
        description="Provides information about symptoms, health conditions, treatments, and procedures using up-to-date web resources.",
        instruction="You are a health agent tasked with providing information about seeking treatments. Use the google_search tool to find information on the web about options.",
    )

    root_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="root_agent",
        description="Healthcare Routing Agent",
        instruction="""
        You are an agent for healthcare services. Your task is to call on one or more sub-agents to answer questions and provide a detailed summary of their answers. Use `health_agent` for general healthcare questions and `policy_agent` for questions on Health Insurance Policies.
        """,
        sub_agents=[health_agent, policy_agent],
    )

    await call_agent_async(
        root_agent,
        "How do I get mental health therapy and what does my insurance cover?",
    )


if __name__ == "__main__":
    asyncio.run(run_hospital_workflow())
