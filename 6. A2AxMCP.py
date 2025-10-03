import warnings

import uvicorn
from dotenv import load_dotenv
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from mcp import StdioServerParameters

warnings.filterwarnings("ignore")

if __name__ == "__main__":
    load_dotenv()
    HOST = "0.0.0.0"
    PORT = 8001

    root_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="root_agent",
        description="Healthcare Provider Agent",
        instruction="""
        You are an agent for healthcare services. Your task is to find providers using the MCP Tool based on the users query.
        """,
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command="uv",
                        args=["run", "mcpserver.py"],
                        env=None,
                    )
                ),
            )
        ],
    )

    # Make your agent A2A-compatible
    a2a_app = to_a2a(root_agent, host=HOST, port=PORT)
    uvicorn.run(a2a_app, host=HOST, port=PORT)
