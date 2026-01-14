import os

import uvicorn
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import google_search

from helpers import setup_env

setup_env()

PORT = int(os.environ.get("RESEARCH_AGENT_PORT"))
HOST = os.environ.get("AGENT_HOST")


def main() -> None:
    # Create the Agent
    root_agent = LlmAgent(
        model="gemini-3-pro-preview",
        name="HealthResearchAgent",
        tools=[google_search],
        description="Provides healthcare information about symptoms, health conditions, treatments, and procedures using up-to-date web resources.",
        instruction="You are a healthcare research agent tasked with providing information about health conditions. Use the google_search tool to find information on the web about options, symptoms, treatments, and procedures. Cite your sources in your responses. Output all of the information you find.",
    )

    # Make the agent A2A-compatible
    a2a_app = to_a2a(root_agent, host=HOST, port=PORT)
    print("Running Health Research Agent")
    uvicorn.run(a2a_app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
