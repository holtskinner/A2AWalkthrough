import asyncio

from agent_framework.a2a import A2AAgent
from rich.console import Console
from rich.markdown import Markdown


async def main() -> None:
    console = Console()
    base_url = "http://localhost:8001"

    # Create A2A agent with direct URL configuration
    healthcare_provider_agent = A2AAgent(
        name="HealthcareProviderAgent",
        url=base_url,
    )

    prompt = "I'm based in Boston, MA. Are there any Psychiatrists near me?"

    result = await healthcare_provider_agent.run(prompt)
    console.print(Markdown(result.text))


if __name__ == "__main__":
    asyncio.run(main())
