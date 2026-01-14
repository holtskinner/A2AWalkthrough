import asyncio
import os
from typing import Any

from beeai_framework.adapters.a2a.agents import A2AAgent
from beeai_framework.adapters.a2a.serve.server import A2AServer, A2AServerConfig
from beeai_framework.adapters.langchain.chat_models import LangChainChatModel
from beeai_framework.agents.requirement import RequirementAgent
from beeai_framework.agents.requirement.requirements.conditional import (
    ConditionalRequirement,
)
from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.middleware.trajectory import EventMeta, GlobalTrajectoryMiddleware
from beeai_framework.serve.utils import LRUMemoryManager
from beeai_framework.tools import Tool
from beeai_framework.tools.handoff import HandoffTool
from beeai_framework.tools.think import ThinkTool
from dotenv import load_dotenv
from langchain_community.chat_models import ChatLiteLLM


# Log only tool calls
class ConciseGlobalTrajectoryMiddleware(GlobalTrajectoryMiddleware):
    def _format_prefix(self, meta: EventMeta) -> str:
        prefix = super()._format_prefix(meta)
        return prefix.rstrip(": ")

    def _format_payload(self, value: Any) -> str:
        return ""


def main() -> None:
    print("Running A2A Orchestrator Agent")
    load_dotenv()

    host = os.environ.get("AGENT_HOST")
    policy_agent_port = os.environ.get("POLICY_AGENT_PORT")
    research_agent_port = os.environ.get("RESEARCH_AGENT_PORT")
    provider_agent_port = os.environ.get("PROVIDER_AGENT_PORT")
    healthcare_agent_port = int(os.environ.get("HEALTHCARE_AGENT_PORT"))

    # Log only tool calls
    GlobalTrajectoryMiddleware(target=[Tool])

    policy_agent = A2AAgent(
        url=f"http://{host}:{policy_agent_port}", memory=UnconstrainedMemory()
    )
    # Run `check_agent_exists()` to fetch and populate AgentCard
    asyncio.run(policy_agent.check_agent_exists())
    print("\tℹ️", f"{policy_agent.name} initialized")

    research_agent = A2AAgent(
        url=f"http://{host}:{research_agent_port}", memory=UnconstrainedMemory()
    )
    asyncio.run(research_agent.check_agent_exists())
    print("\tℹ️", f"{research_agent.name} initialized")

    provider_agent = A2AAgent(
        url=f"http://{host}:{provider_agent_port}", memory=UnconstrainedMemory()
    )
    asyncio.run(provider_agent.check_agent_exists())
    print("\tℹ️", f"{provider_agent.name} initialized")

    healthcare_agent = RequirementAgent(
        name="Healthcare Agent",
        description="A personal concierge for Healthcare Information, customized to your policy.",
        llm=LangChainChatModel(ChatLiteLLM(model="gemini/gemini-1.5-flash")),
        tools=[
            thinktool := ThinkTool(),
            policy_tool := HandoffTool(
                target=policy_agent,
                name=policy_agent.name,
                description=policy_agent.agent_card.description,
            ),
            research_tool := HandoffTool(
                target=research_agent,
                name=research_agent.name,
                description=research_agent.agent_card.description,
            ),
            provider_tool := HandoffTool(
                target=provider_agent,
                name=provider_agent.name,
                description=provider_agent.agent_card.description,
            ),
        ],
        requirements=[
            ConditionalRequirement(policy_tool, consecutive_allowed=False),
            ConditionalRequirement(
                thinktool, force_at_step=1, force_after=Tool, consecutive_allowed=False
            ),
        ],
        role="Healthcare Concierge",
        instructions=(
            f"""You are a concierge for healthcare services. Your task is to handoff to one or more agents to answer questions and provide a detailed summary of their answers. Be sure that all of their questions are answered before responding.

            IMPORTANT: When returning answers about providers, only output providers from `{provider_agent.name}` and only provide insurance information based on the results from `{policy_agent.name}`.

            In your output, put which agent gave you the information!"""
        ),
    )

    print("\tℹ️", f"{healthcare_agent.meta.name} initialized")

    # Register the agent with the A2A server and run the HTTP server
    # we use LRU memory manager to keep limited amount of sessions in the memory
    A2AServer(
        config=A2AServerConfig(
            port=healthcare_agent_port, protocol="jsonrpc", host=host
        ),
        memory_manager=LRUMemoryManager(maxsize=100),
    ).register(healthcare_agent, send_trajectory=True).serve()


if __name__ == "__main__":
    main()
