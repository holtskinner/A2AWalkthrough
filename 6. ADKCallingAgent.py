# Import the implementation from the file
import asyncio

from google.adk.agents import Agent
from google.adk.agents.llm_agent import Agent
from google.adk.agents.remote_a2a_agent import (
    AGENT_CARD_WELL_KNOWN_PATH,
    RemoteA2aAgent,
)
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


async def call_agent_async(query: str, runner, user_id, session_id):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User Query: {query}")

    # Prepare the user's message in ADK format
    content = types.Content(role="user", parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response."  # Default

    # Key Concept: run_async executes the agent logic and yields Events.
    # We iterate through events to find the final answer.
    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=content
    ):
        # You can uncomment the line below to see *all* events during execution
        # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

        # Key Concept: is_final_response() marks the concluding message for the turn.
        if event.is_final_response():
            if event.content and event.content.parts:
                # Assuming text response in the first part
                final_response_text = event.content.parts[0].text
            elif (
                event.actions and event.actions.escalate
            ):  # Handle potential errors/escalations
                final_response_text = (
                    f"Agent escalated: {event.error_message or 'No specific message.'}"
                )
            # Add more checks here if needed (e.g., specific error codes)
            break  # Stop processing events once the final response is found

    print(f"<<< Agent Response: {final_response_text}")


async def run_hospital_workflow() -> None:

    policy_agent = RemoteA2aAgent(
        name="policy_agent",
        agent_card=(f"http://0.0.0.0:9999{AGENT_CARD_WELL_KNOWN_PATH}"),
    )
    health_agent = RemoteA2aAgent(
        name="health_agent",
        agent_card=(f"http://0.0.0.0:9998{AGENT_CARD_WELL_KNOWN_PATH}"),
    )

    root_agent = Agent(
        model="gemini-2.5-flash-lite",
        name="root_agent",
        instruction="""
        You are an agent for healthcare services. Your task is to call on one or more sub-agents to answer questions and provide a detailed summary of their answers. Use `health_agent` for general healthcare questions and `policy_agent` for questions on Health Insurance Policies.
        """,
        sub_agents=[policy_agent, health_agent],
    )

    session_service = InMemorySessionService()

    APP_NAME = "health_app"
    USER_ID = "user_1"
    SESSION_ID = "session_001"  # Using a fixed ID for simplicity

    # Create the specific session where the conversation will happen
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    print(
        f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'"
    )

    # --- Runner ---
    # Key Concept: Runner orchestrates the agent execution loop.
    runner = Runner(
        agent=root_agent,  # The agent we want to run
        app_name=APP_NAME,  # Associates runs with our app
        session_service=session_service,  # Uses our session manager
    )
    print(f"Runner created for agent '{runner.agent.name}'.")

    await call_agent_async(
        "what does my insurance cover for mental health therapy and how do I find a therapist?",
        runner=runner,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )


if __name__ == "__main__":
    asyncio.run(run_hospital_workflow())
