import os

import uvicorn
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

if __name__ == "__main__":
    load_dotenv()

    HOST = "localhost"
    PORT = 9997

    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = "us-east5"

    model = GoogleModel(
        "meta/llama-4-scout-17b-16e-instruct-maas",
        provider=GoogleProvider(vertexai=True, project=project_id, location=location),
    )

    # Connect to MCP Server
    server = MCPServerStdio(
        "uv",
        args=["run", "mcpserver.py"],
        timeout=10,
        id="healthcare_providers",
    )

    agent = Agent(
        model,
        instructions="""You are a healthcare assistant. Your task is to find healthcare providers using the healthcare_providers MCP Tool based on the user's query. Output all relevant information for the user.""",
        toolsets=[server],
    )
    app = agent.to_a2a(url=f"http://{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)
