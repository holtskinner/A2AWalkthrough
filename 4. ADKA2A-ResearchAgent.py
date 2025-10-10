import warnings

import uvicorn
from dotenv import load_dotenv
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents import LlmAgent
from google.adk.tools import google_search

warnings.filterwarnings("ignore")

if __name__ == "__main__":
    load_dotenv()
    PORT = 9998
    HOST = "localhost"

    root_agent = LlmAgent(
        model="gemini-2.5-pro",
        name="HealthResearchAgent",
        tools=[google_search],
        description="Provides healthcare information about symptoms, health conditions, treatments, and procedures using up-to-date web resources.",
        instruction="You are a healthcare research agent tasked with providing information health conditions. Use the google_search tool to find information on the web about options.",
    )

    # Make your agent A2A-compatible
    a2a_app = to_a2a(root_agent, host=HOST, port=PORT)
    uvicorn.run(a2a_app, host=HOST, port=PORT)
