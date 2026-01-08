from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_community.chat_models import ChatLiteLLM
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import StdioConnection


class ProviderAgent:
    def __init__(self) -> None:
        load_dotenv()
        self.mcp_client = MultiServerMCPClient(
            {
                "find_healthcare_providers": StdioConnection(
                    transport="stdio",
                    command="uv",
                    args=["run", "mcpserver.py"],
                )
            }
        )
        self.agent = None

    async def initialize(self):
        """Initialize the agent asynchronously."""
        tools = await self.mcp_client.get_tools()
        self.agent = create_agent(
            ChatLiteLLM(
                model="gemini/gemini-1.5-flash",
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
