import asyncio
import os
import sys
import traceback

from beeai_framework.adapters.a2a import A2AServer, A2AServerConfig
from beeai_framework.adapters.a2a.agents import A2AAgent
from beeai_framework.adapters.vertexai import VertexAIChatModel
from beeai_framework.agents.requirement import RequirementAgent
from beeai_framework.agents.requirement.requirements.conditional import (
    ConditionalRequirement,
)
from beeai_framework.errors import FrameworkError
from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.memory.unconstrained_memory import UnconstrainedMemory
from beeai_framework.serve.utils import LRUMemoryManager
from beeai_framework.tools.handoff import HandoffTool
from beeai_framework.tools.think import ThinkTool
from dotenv import load_dotenv

from helpers import authenticate


def main() -> None:
    print("Running General Healthcare Agent")

    load_dotenv()
    _, project_id = authenticate()

    host = os.environ.get("AGENT_HOST")
    policy_port = os.environ.get("POLICY_AGENT_PORT")
    research_port = os.environ.get("RESEARCH_AGENT_PORT")
    provider_port = os.environ.get("PROVIDER_AGENT_PORT")
    healthcare_agent_port = int(os.environ.get("HEALTHCARE_AGENT_PORT"))

    print("ℹ️", "Initializing agents and tools")

    policy_agent = A2AAgent(
        url=f"http://{host}:{policy_port}", memory=UnconstrainedMemory()
    )
    # Run `check_agent_exists()` to populate AgentCard
    asyncio.run(policy_agent.check_agent_exists())
    print("\tℹ️", f"{policy_agent.name} initialized")

    research_agent = A2AAgent(
        url=f"http://{host}:{research_port}", memory=UnconstrainedMemory()
    )
    asyncio.run(research_agent.check_agent_exists())

    print("\tℹ️", f"{research_agent.name} initialized")

    provider_agent = A2AAgent(
        url=f"http://{host}:{provider_port}", memory=UnconstrainedMemory()
    )
    asyncio.run(provider_agent.check_agent_exists())

    print("\tℹ️", f"{provider_agent.name} initialized")

    healthcare_agent = RequirementAgent(
        name="Healthcare Agent",
        description="A personal concierge for Healthcare Information, customized to your policy.",
        llm=VertexAIChatModel(
            model_id="gemini-2.5-flash",
            project=project_id,
            location="global",
            allow_parallel_tool_calls=True,
        ),
        tools=[
            ThinkTool(),
            HandoffTool(
                policy_agent,
                name=policy_agent.name,
                description=policy_agent.agent_card.name,
            ),
            HandoffTool(
                research_agent,
                name=research_agent.name,
                description=research_agent.agent_card.description,
            ),
            HandoffTool(
                provider_agent,
                name=provider_agent.name,
                description=provider_agent.agent_card.description,
            ),
        ],
        requirements=[
            ConditionalRequirement(ThinkTool, consecutive_allowed=False),
            # AskPermissionRequirement([research_agent.name, policy_agent.name]),
        ],
        role="Healthcare Concierge",
        instructions=(
            f"""You are a concierge for healthcare services. Your task is to handoff to one or more agents to answer questions and provide a detailed summary of their answers. First, use `{research_agent.name}` for research about their condition. Provide this research to the user. Then use `{policy_agent.name}` for information about their specific Health Insurance Policy And use `{provider_agent.name}` for finding providers in their location.

            IMPORTANT: When returning answers about providers, only output providers from `{provider_agent.name}` and only provide insurance information based on the results from `{policy_agent.name}`.

            In your output, put which agent gave you the information."""
        ),
        notes=[
            "If user does not provide a valid healthcare-related question, use 'final_answer' tool for clarification."
        ],
    )

    print("\tℹ️", f"{healthcare_agent.meta.name} initialized")

    # Register the agent with the A2A server and run the HTTP server
    # we use LRU memory manager to keep limited amount of sessions in the memory
    server = A2AServer(
        config=A2AServerConfig(host=host, port=healthcare_agent_port),
        memory_manager=LRUMemoryManager(maxsize=100),
    ).register(healthcare_agent)

    server.serve()


if __name__ == "__main__":
    try:
        main()
    except FrameworkError as e:
        print("🛑", f"Fatal framework error: {e!s}")
        traceback.print_exc()
        sys.exit(e.explain())
    except KeyboardInterrupt:
        print("ℹ️", "Application terminated by user")
        print("ℹ️", "Exiting chat...")
        sys.exit(0)
