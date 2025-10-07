import asyncio
from uuid import uuid4

import httpx
from a2a.client.card_resolver import A2ACardResolver
from a2a.client.client_factory import ClientConfig, ClientFactory
from a2a.client.transports.jsonrpc import JsonRpcTransport
from a2a.types import (
    AgentCard,
    Message,
    Part,
    Role,
    TaskQueryParams,
    TextPart,
)
from rich.console import Console, Group
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table


def print_agent_card(console: Console, agent_card: AgentCard) -> None:
    skills_table = Table(title="Skills", show_header=True, header_style="bold magenta")
    skills_table.add_column("Name", style="dim", width=20)
    skills_table.add_column("Description")
    skills_table.add_column("Examples")

    if agent_card.skills:
        for skill in agent_card.skills:
            # Format examples for better display within the table cell
            examples_str = (
                "\n".join(f"• {ex}" for ex in skill.examples)
                if skill.examples
                else "N/A"
            )
            skills_table.add_row(skill.name, skill.description, examples_str)

    # Create the main content string with rich markup
    main_info = (
        f"[bold]Name:[/] [green]{agent_card.name}[/]\n"
        f"[bold]Description:[/] {agent_card.description}\n"
        f"[bold]Version:[/] {agent_card.version}\n"
        f"[bold]URL:[/] [cyan]{agent_card.url}[/]\n"
        f"[bold]Protocol Version:[/] {agent_card.protocol_version}"
    )

    # Create and print the final panel
    agent_card_panel = Panel(
        Group(main_info, skills_table),
        title="[bold yellow]Agent Card Details[/]",
        border_style="blue",
        expand=False,
    )
    console.print(agent_card_panel)


async def poll_task(client: JsonRpcTransport, task_id: str) -> str | None:
    """Polls a task status iteratively until it reaches a terminal state."""
    while True:
        task = await client.get_task(request=TaskQueryParams(id=task_id))
        state = task.status.state

        if state in {"completed", "failed", "cancelled"}:
            if state == "completed":
                if task.history:
                    last_message = task.history[-1]
                    if last_message.role == "agent" and last_message.parts:
                        return last_message.parts[0].root.text
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
        agent_card = await A2ACardResolver(
            httpx_client=httpx_client, base_url=base_url
        ).get_agent_card()
        print_agent_card(console, agent_card)

        client = ClientFactory(
            config=ClientConfig(polling=True, httpx_client=httpx_client)
        ).create(agent_card)

        message = Message(
            message_id=uuid4().hex,
            role=Role.user,
            parts=[Part(TextPart(text=prompt))],
        )

        console.print(f"\n[bold]Sending prompt:[/] '{prompt}' to the agent...")
        responses = client.send_message(message)

        text_content = ""
        async for response in responses:
            if response.kind == "message":
                message_id = response.message_id
                text_content = response.parts[0].root.text

                console.print(f"[yellow]Message ID:[/] {message_id}")
            elif response.kind == "artifact":
                artifact_id = response.artifacts[0].artifact_id
                text_content = response.artifacts[0].parts[0].root.text

                console.print(f"[yellow]Artifact ID:[/] {artifact_id}")
            elif response.kind == "task":
                text_content = await poll_task(client, response.id)

        console.print("\n[bold green]Final Agent Response:[/]")
        if text_content:
            console.print(Markdown(text_content))
        else:
            console.print("[red]No final text content received.[/]")


if __name__ == "__main__":
    asyncio.run(main())
