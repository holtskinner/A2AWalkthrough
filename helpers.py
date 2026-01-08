import os

import nest_asyncio
from IPython.display import IFrame, Markdown, display
from a2a.types import AgentCard
from dotenv import load_dotenv


def setup_env():
    """Initializes the environment by loading .env and applying nest_asyncio."""
    load_dotenv(override=True)
    nest_asyncio.apply()


def display_terminal(terminal_id: int, height: int = 600):
    """Displays a terminal IFrame in the notebook."""
    url = os.environ.get("DLAI_LOCAL_URL", "http://localhost:8888/").format(port=8888)
    display(IFrame(f"{url}terminals/{terminal_id}", width=800, height=height))


def display_agent_card(agent_card: AgentCard) -> None:
    """Nicely formats and displays an AgentCard."""

    def esc(text: str) -> str:
        """Escapes pipe characters for Markdown table compatibility."""
        return str(text).replace("|", r"\|")

    # --- Part 1: Main Metadata Table ---
    md_parts = [
        "### Agent Card Details",
        "| Property | Value |",
        "| :--- | :--- |",
        f"| **Name** | {esc(agent_card.name)} |",
        f"| **Description** | {esc(agent_card.description)} |",
        f"| **Version** | `{esc(agent_card.version)}` |",
        f"| **URL** | [{esc(agent_card.url)}]({agent_card.url}) |",
        f"| **Protocol Version** | `{esc(agent_card.protocol_version)}` |",
    ]

    # --- Part 2: Skills Table ---
    if agent_card.skills:
        md_parts.extend(
            [
                "\n#### Skills",
                "| Name | Description | Examples |",
                "| :--- | :--- | :--- |",
            ]
        )
        for skill in agent_card.skills:
            examples_str = (
                "<br>".join(f"• {esc(ex)}" for ex in skill.examples)
                if skill.examples
                else "N/A"
            )
            md_parts.append(
                f"| **{esc(skill.name)}** | {esc(skill.description)} | {examples_str} |"
            )

    # Join all parts and display
    display(Markdown("\n".join(md_parts)))
