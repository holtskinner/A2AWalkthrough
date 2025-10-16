import asyncio
import os

import httpx
from a2a.client import (
    A2ACardResolver,
    Client,
    ClientConfig,
    ClientFactory,
    create_text_message_object,
)
from a2a.types import (
    AgentCard,
    Artifact,
    Message,
)
from a2a.utils.message import get_message_text
from dotenv import load_dotenv
from rich.console import Console, Group
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table


def print_agent_card(console: Console, agent_card: AgentCard) -> None:
    """Displays the agent card details in a formatted panel."""
    main_info = (
        f"[bold]Name:[/] [green]{agent_card.name}[/]\n"
        f"[bold]Description:[/] {agent_card.description}\n"
        f"[bold]Version:[/] {agent_card.version}\n"
        f"[bold]URL:[/] [cyan]{agent_card.url}[/]\n"
        f"[bold]Protocol Version:[/] {agent_card.protocol_version}"
    )
    group = Group(main_info)

    if agent_card.skills:
        skills_table = Table(
            title="Skills", show_header=True, header_style="bold magenta"
        )
        skills_table.add_column("Name", style="dim", width=20)
        skills_table.add_column("Description")
        skills_table.add_column("Examples")

        for skill in agent_card.skills:
            examples_str = (
                "\n".join(f"• {ex}" for ex in skill.examples)
                if skill.examples
                else "N/A"
            )
            skills_table.add_row(skill.name, skill.description, examples_str)
        group.renderables.append(skills_table)

    agent_card_panel = Panel(
        group,
        title="[bold yellow]Agent Card Details[/]",
        border_style="blue",
        expand=False,
    )
    console.print(agent_card_panel)


async def main() -> None:
    load_dotenv()

    host = os.environ.get("AGENT_HOST", "localhost")
    port = os.environ.get("POLICY_AGENT_PORT", 9999)
    base_url = f"http://{host}:{port}"

    prompt = "How much would I pay for mental health therapy?"
    console = Console()

    async with httpx.AsyncClient(timeout=100.0) as httpx_client:
        # Step 1: Discover the agent by fetching its card
        agent_card = await A2ACardResolver(
            httpx_client=httpx_client, base_url=base_url
        ).get_agent_card()
        print_agent_card(console, agent_card)

        # Step 2: Create a client
        client_factory = ClientFactory(
            config=ClientConfig(
                httpx_client=httpx_client,
                streaming=True,
            )
        )
        client: Client = client_factory.create(agent_card)

        # Step 3: Create the message using a convenient helper function
        message = create_text_message_object(content=prompt)

        console.print(f"\n[bold]Sending prompt:[/] '{prompt}' to the agent...")

        # Step 4: Send the message and await the final response.
        responses = client.send_message(message)

        text_content = ""

        # Step 5: Process the responses from the agent
        async for response in responses:
            if isinstance(response, Message):
                # The agent replied directly with a final message
                console.print(f"[yellow]Message ID:[/] {response.message_id}")
                text_content = get_message_text(response)
            elif isinstance(response, Artifact):
                artifact_id = response.artifact_id
                console.print(f"[yellow]Artifact ID:[/] {artifact_id}")
                text_content = get_message_text(response)
            elif isinstance(response, tuple):  # It's a ClientEvent (Task, update)
                console.print(f"[yellow]Task ID:[/] {response[0].id}")
                text_content = get_message_text(response[0].artifacts[0])
        console.print("\n[bold green]Final Agent Response:[/]")
        if text_content:
            console.print(Markdown(text_content))
        else:
            console.print(
                "[red]No final text content received or task did not complete successfully.[/]"
            )


if __name__ == "__main__":
    asyncio.run(main())
