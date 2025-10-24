import asyncio
import os

from agent_framework.a2a import A2AAgent
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown


async def main() -> None:
    load_dotenv()
    host = os.environ.get("AGENT_HOST")
    port = os.environ.get("PROVIDER_AGENT_PORT")
    base_url = f"http://{host}:{port}"

    console = Console()

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
