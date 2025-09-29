from crewai import LLM, Agent, Crew, Task
from crewai_tools import RagTool

llm = LLM(model="ollama_chat/qwen2.5:14b", base_url="http://localhost:11434", max_tokens=8192)
config = {
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "qwen2.5:14b",
        }
    },
    "embedding_model": {
        "provider": "ollama",
        "config": {
            "model": "all-minilm:latest"
        }
    }
}

rag_tool = RagTool(config=config)
rag_tool.add("./data/gold-hospital-and-premium-extras.pdf", data_type="pdf_file")

insurance_agent = Agent(
    role="Senior Insurance Coverage Assistant",
    goal="Determine whether something is covered or not",
    backstory="You are an expert insurance agent designed to assist with coverage queries",
    verbose=True,
    allow_delegation=False,
    llm=llm,
    tools=[rag_tool],
    max_retry_limit=5,
)

task1 = Task(
    description="What is the waiting period for rehabilitation?",
    expected_output="A comprehensive response as to the users question",
    agent=insurance_agent,
)
crew = Crew(agents=[insurance_agent], tasks=[task1], verbose=True)

task_output = crew.kickoff()
