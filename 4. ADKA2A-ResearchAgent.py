import os
import warnings

import uvicorn
from dotenv import load_dotenv
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents import LlmAgent
from google.adk.tools import google_search

from helpers import authenticate

warnings.filterwarnings("ignore")

if __name__ == "__main__":
    print("Running Healthcare Research Agent")
    load_dotenv()
    authenticate()
    PORT = int(os.environ.get("RESEARCH_AGENT_PORT"))
    HOST = os.environ.get("AGENT_HOST")

    root_agent = LlmAgent(
        model="gemini-2.5-pro",
        name="HealthResearchAgent",
        tools=[google_search],
        description="Provides healthcare information about symptoms, health conditions, treatments, and procedures using up-to-date web resources.",
        instruction="You are a healthcare research agent tasked with providing information about health conditions. Use the google_search tool to find information on the web about options, symptoms, treatments, and procedures. Cite your sources in your responses. Output all of the information you find.",
    )

    # Make your agent A2A-compatible
    a2a_app = to_a2a(root_agent, host=HOST, port=PORT)
    uvicorn.run(a2a_app, host=HOST, port=PORT)
