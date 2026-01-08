from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import StdioConnection
from langchain_openai import ChatOpenAI

from helpers import authenticate


class ProviderAgent:
    def __init__(self) -> None:
        credentials, project_id = authenticate()
        location = "us-central1"
        base_url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/endpoints/openapi"

        self.mcp_client = MultiServerMCPClient(
            {
                "find_healthcare_providers": StdioConnection(
                    transport="stdio",
                    command="uv",
                    args=["run", "mcpserver.py"],
                )
            }
        )

        self.credentials = credentials
        self.base_url = base_url
        self.agent = None

    async def initialize(self):
        """Initialize the agent asynchronously."""
        tools = await self.mcp_client.get_tools()
        self.agent = create_agent(
            ChatOpenAI(
                model="openai/gpt-oss-20b-maas",
                openai_api_key=self.credentials.token,
                openai_api_base=self.base_url,
            ),
            tools,
            name="HealthcareProviderAgent",
            system_prompt="Your task is to find and list providers using the find_healthcare_providers MCP Tool based on the users query. Only use providers based on the response from the tool. Output the information in a table.",
        )
        return self

    async def answer_query(self, prompt: str) -> str:
        if self.agent is None:
            raise RuntimeError("Agent not initialized. Call initialize() first.")

        response = await self.agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ]
            }
        )
        return response["messages"][-1].content
