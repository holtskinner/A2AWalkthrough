import asyncio

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
    Message,
    TaskQueryParams,
)
from a2a.utils.message import get_message_text
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


async def poll_task(client: Client, task_id: str) -> str | None:
    """Polls a task status iteratively until it reaches a terminal state."""
    while True:
        task = await client.get_task(request=TaskQueryParams(id=task_id))
        state = task.status.state

        if state in {"completed", "failed", "cancelled"}:
            if state == "completed":
                if task.history:
                    last_message = task.history[-1]
                    if last_message.role == "agent":
                        return get_message_text(last_message)
            elif state == "failed":
                print("Task failed")
            elif state == "cancelled":
                print("Task cancelled")

            return None

        await asyncio.sleep(1)


async def main() -> None:
    base_url = "http://localhost:9999"
    prompt = "How much would I pay for mental health therapy?"
    console = Console()

    async with httpx.AsyncClient(timeout=100.0) as httpx_client:
        # Step 1: Discover the agent by fetching its card
        agent_card = await A2ACardResolver(
            httpx_client=httpx_client, base_url=base_url
        ).get_agent_card()
        print_agent_card(console, agent_card)

        # Step 2: Create a client. By leaving polling=False (the default), the
        # client will ask the server to wait for the task to complete. This
        # removes the need for a manual polling loop.
        client_factory = ClientFactory(config=ClientConfig(httpx_client=httpx_client))
        client: Client = client_factory.create(agent_card)

        # Step 3: Create the message using a convenient helper function
        message = create_text_message_object(content=prompt)

        console.print(f"\n[bold]Sending prompt:[/] '{prompt}' to the agent...")

        # Step 4: Send the message and await the final response.
        # Since we are not polling, the `send_message` async iterator will
        # yield exactly one item: the final result.
        responses = client.send_message(message)

        text_content = ""

        # Step 5: Process the responses from the agent

        async for response in responses:
            if isinstance(response, Message):
                # The agent replied directly with a final message

                console.print(f"[yellow]Message ID:[/] {response.message_id}")
                text_content = get_message_text(response)
            elif isinstance(response, tuple):  # It's a ClientEvent (Task, update)
                # The agent completed a task. The final answer is in the task history.

                text_content = await poll_task(client, response[0].id)
        console.print("\n[bold green]Final Agent Response:[/]")
        if text_content:
            console.print(Markdown(text_content))
        else:
            console.print(
                "[red]No final text content received or task did not complete successfully.[/]"
            )


if __name__ == "__main__":
    asyncio.run(main())
