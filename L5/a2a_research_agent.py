import logging
import os
import warnings

import uvicorn
from dotenv import load_dotenv
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents import LlmAgent
from google.adk.tools import google_search

from helpers import authenticate

logging.disable(level=logging.WARNING)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

load_dotenv()

# Authenticate
credentials, project_id = authenticate(location="global")

PORT = int(os.environ.get("RESEARCH_AGENT_PORT"))
HOST = os.environ.get("AGENT_HOST")

root_agent = LlmAgent(
    model="gemini-2.5-pro",
    name="HealthResearchAgent",
    tools=[google_search],
    description="Provides healthcare information about symptoms, health conditions, treatments, and procedures using up-to-date web resources.",
    instruction="You are a healthcare research agent tasked with providing information about health conditions. Use the google_search tool to find information on the web about options, symptoms, treatments, and procedures. Cite your sources in your responses. Output all of the information you find.",
)


def main():
    # Make your agent A2A-compatible
    a2a_app = to_a2a(root_agent, host=HOST, port=PORT)
    print("Running Health Research Agent")
    uvicorn.run(a2a_app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
