import asyncio

from acp_sdk.client import Client
from colorama import Fore


async def run_hospital_workflow() -> None:
    async with Client(base_url="http://localhost:8000") as hospital:
        run1 = await hospital.run_sync(
            agent="health_agent",
            input="I'm based in Atlanta,GA. Are there any Cardiologists near me?",
        )
        content = run1.output[0].parts[0].content
        print(Fore.LIGHTMAGENTA_EX + content + Fore.RESET)


if __name__ == "__main__":
    asyncio.run(run_hospital_workflow())
