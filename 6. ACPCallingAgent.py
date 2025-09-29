# Import the implementation from the file
import asyncio

from acp_sdk.client import Client
from colorama import Fore
from smolagents import LiteLLMModel

from fastacp import ACPCallingAgent, AgentCollection

model = LiteLLMModel(model_id="ollama_chat/qwen2.5:14b", num_ctx=8192)


async def run_hospital_workflow() -> None:
    async with (
        Client(base_url="http://localhost:8001") as insurer,
        Client(base_url="http://localhost:8000") as hospital,
    ):
        agent_collection = await AgentCollection.from_acp(insurer, hospital)
        acp_agents = {
            agent.name: {"agent": agent, "client": client}
            for client, agent in agent_collection.agents
        }
        print(acp_agents)
        acpagent = ACPCallingAgent(acp_agents=acp_agents, model=model)
        result = await acpagent.run(
            "do i need rehabilitation after a shoulder reconstruction and what is the waiting period from my insurance?"
        )
        print(Fore.YELLOW + f"Final result: {result}" + Fore.RESET)


if __name__ == "__main__":
    asyncio.run(run_hospital_workflow())
