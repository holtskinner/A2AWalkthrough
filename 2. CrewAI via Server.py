from collections.abc import AsyncGenerator

from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Context, RunYield, RunYieldResume, Server
from crewai import LLM, Agent, Crew, Task
from crewai_tools import RagTool

llm = LLM(
    model="ollama_chat/qwen2.5:14b", base_url="http://localhost:11434", max_tokens=8192
)
config = {
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "qwen2.5:14b",
        },
    },
    "embedding_model": {"provider": "ollama", "config": {"model": "all-minilm:latest"}},
}

rag_tool = RagTool(config=config)
rag_tool.add("./data/gold-hospital-and-premium-extras.pdf", data_type="pdf_file")

insurance_agent = Agent(
    role="Senior Insurance Coverage Assistant",
    goal="Determine whether something is covered or not",
    backstory="""You are an expert insurance agent designed to assist with coverage queries. Whenever you call the knowledge base tool the tool input must follow the pattern
        {query: 'your query', kwargs:{'}}"
    """,
    verbose=True,
    allow_delegation=False,
    llm=llm,
    tools=[rag_tool],
    max_retry_limit=5,
)

rag_tool
import logging

logger = logging.getLogger(__name__)

server = Server()


@server.agent()
async def policy_agent(
    input: list[Message], context: Context
) -> AsyncGenerator[RunYield, RunYieldResume]:
    """This is an agent for questions around policy coverage, it uses a RAG pattern to find answers based on policy documentation. Use it to help answer questions on coverage and waiting periods."""
    task1 = Task(
        description=input[0].parts[0].content,
        expected_output="A comprehensive response as to the users question",
        agent=insurance_agent,
    )
    crew = Crew(agents=[insurance_agent], tasks=[task1], verbose=True)

    task_output = await crew.kickoff_async()
    logger.info("Task completed successfully")
    logger.info(task_output)
    yield Message(parts=[MessagePart(content=str(task_output))])


if __name__ == "__main__":
    server.run(port=8001)
