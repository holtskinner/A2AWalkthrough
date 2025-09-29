from collections.abc import AsyncGenerator

from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Context, RunYield, RunYieldResume, Server
from mcp import StdioServerParameters
from smolagents import (
    LiteLLMModel,
    ToolCallingAgent,
    ToolCollection,
)

server = Server()

model = LiteLLMModel(
    model_id="ollama_chat/qwen2.5:14b",
    api_base="http://localhost:11434",
    api_key="your-api-key",
    num_ctx=8192,
)

# Outline STDIO stuff to get to MCP Tools
server_parameters = StdioServerParameters(
    command="uv",
    args=["run", "mcpserver.py"],
    env=None,
)


@server.agent()
async def health_agent(
    input: list[Message], context: Context
) -> AsyncGenerator[RunYield, RunYieldResume]:
    """This is a CodeAgent which supports the hospital to handle health based questions for patients. Current or prospective patients can use it to find answers about their health and hospital treatments."""
    with ToolCollection.from_mcp(
        server_parameters, trust_remote_code=True
    ) as tool_collection:
        agent = ToolCallingAgent(tools=[*tool_collection.tools], model=model)
        prompt = input[0].parts[0].content
        response = agent.run(prompt)

    yield Message(parts=[MessagePart(content=str(response))])


if __name__ == "__main__":
    server.run()
