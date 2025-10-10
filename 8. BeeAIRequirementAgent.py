import asyncio
import os
import sys
import traceback

from beeai_framework.adapters.a2a import A2AServer, A2AServerConfig
from beeai_framework.adapters.a2a.agents import A2AAgent, A2AAgentUpdateEvent
from beeai_framework.adapters.vertexai import VertexAIChatModel
from beeai_framework.agents.requirement import RequirementAgent
from beeai_framework.agents.requirement.requirements import Requirement
from beeai_framework.agents.requirement.requirements.ask_permission import (
    AskPermissionRequirement,
)
from beeai_framework.agents.requirement.requirements.conditional import (
    ConditionalRequirement,
)
from beeai_framework.emitter import EventMeta
from beeai_framework.errors import FrameworkError
from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.memory.unconstrained_memory import UnconstrainedMemory
from beeai_framework.middleware.trajectory import GlobalTrajectoryMiddleware
from beeai_framework.serve.utils import LRUMemoryManager
from beeai_framework.tools.handoff import HandoffTool
from beeai_framework.tools.think import ThinkTool
from dotenv import load_dotenv


def print_update(data: A2AAgentUpdateEvent, event: EventMeta) -> None:
    value = data.value
    debug_info = value[1] if isinstance(value, tuple) else value
    print("Agent 🤖 (debug) : ", str(debug_info))


async def main() -> None:
    load_dotenv()
    host = os.environ.get("AGENT_HOST", "localhost")
    policy_port = os.environ.get("POLICY_AGENT_PORT", 9999)
    research_port = os.environ.get("RESEARCH_AGENT_PORT", 9998)
    provider_port = os.environ.get("PROVIDER_AGENT_PORT", 8001)

    prompt = "I'm based in Boston, MA. How do I get mental health therapy near me and what does my insurance cover?"
    print("ℹ️", "Initializing agents and tools")

    policy_agent = A2AAgent(
        url=f"http://{host}:{policy_port}", memory=UnconstrainedMemory()
    )
    # Run `check_agent_exists()` to populate AgentCard
    # asyncio.run(policy_agent.check_agent_exists())
    await policy_agent.check_agent_exists()
    print("\tℹ️", f"{policy_agent.name} initialized")

    research_agent = A2AAgent(
        url=f"http://{host}:{research_port}", memory=UnconstrainedMemory()
    )
    # asyncio.run(research_agent.check_agent_exists())

    await research_agent.check_agent_exists()
    print("\tℹ️", f"{research_agent.name} initialized")

    provider_agent = A2AAgent(
        url=f"http://{host}:{provider_port}", memory=UnconstrainedMemory()
    )
    # asyncio.run(provider_agent.check_agent_exists())

    await provider_agent.check_agent_exists()
    print("\tℹ️", f"{provider_agent.name} initialized")

    healthcare_agent = RequirementAgent(
        name="Healthcare Agent",
        description="A personal concierge for Healthcare Information, customized to your policy.",
        llm=VertexAIChatModel(
            model_id="gemini-2.5-flash",
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
            # ConditionalRequirement(ThinkTool, consecutive_allowed=False),
            AskPermissionRequirement([policy_agent.name, research_agent.name]),
        ],
        role="Healthcare Concierge",
        instructions=(
            f"""You are a concierge for healthcare services. Your task is to handoff to one or more agents to answer questions and provide a detailed summary of their answers. First, use `{research_agent.name}` for research about conditions and treatment options. Then use `{provider_agent.name}` for finding providers in their State, and `{policy_agent.name}` for questions on Health Insurance Policies. In your output, put which agent gave you the information."""
        ),
        notes=[
            "If user does not provide a valid healthcare-related question, use 'final_answer' tool for clarification."
        ],
    )

    print("\tℹ️", f"{healthcare_agent.meta.name} initialized")

    # Register the agent with the A2A server and run the HTTP server
    # we use LRU memory manager to keep limited amount of sessions in the memory
    # server = A2AServer(
    #     config=A2AServerConfig(host="localhost", port=9997),
    #     memory_manager=LRUMemoryManager(maxsize=100),
    # ).register(healthcare_agent)

    # server.serve()

    try:
        response = (
            await healthcare_agent.run(
                prompt,
                total_max_retries=3,
                max_retries_per_step=1,
                max_iterations=10,
            )
            .on("update", print_update)
            .middleware(GlobalTrajectoryMiddleware(excluded=[Requirement]))
        )

        print("Agent 🤖 : ", response.last_message.text)
    except FrameworkError as e:
        print("❌ Error:", e.explain())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except FrameworkError as e:
        print("🛑", f"Fatal framework error: {e!s}")
        traceback.print_exc()
        sys.exit(e.explain())
    except KeyboardInterrupt:
        print("ℹ️", "Application terminated by user")
        print("ℹ️", "Exiting chat...")
        sys.exit(0)
