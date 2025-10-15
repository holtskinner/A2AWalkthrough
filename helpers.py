import os
import sys

from rich.console import Console
from rich.markdown import Markdown


class ConsoleReader:

    def __init__(
        self,
        *,
        fallback: str = "",
        input_prompt: str = "User 👤 : ",
        allow_empty: bool = False,
    ) -> None:
        self.console = Console()
        self.fallback = fallback
        self.input_prompt = input_prompt
        self.allow_empty = allow_empty

    def __iter__(self) -> "ConsoleReader":
        self.console.print(
            "[yellow]Interactive session has started. To escape, input 'q' and submit.[/yellow]"
        )
        return self

    def __next__(self) -> str:
        try:
            while True:
                prompt = self.console.input(
                    f"[bold cyan]{self.input_prompt}[/]"
                ).strip()

                if not sys.stdin.isatty() and "PYCHARM_HOSTED" not in os.environ:
                    print(prompt)

                if prompt.lower() == "q":
                    raise StopIteration

                prompt = prompt if prompt else self.fallback

                if not prompt and not self.allow_empty:
                    self.console.print(
                        "[bold red]Error:[/] Empty prompt is not allowed. Please try again."
                    )
                    continue

                return prompt
        except (EOFError, KeyboardInterrupt):
            self.console.print("\n[bold yellow]Exiting session.[/bold yellow]")
            raise StopIteration

    def write(self, role: str, data: str) -> None:
        markdown_content = Markdown(f"**{role}**\n\n---\n{data}")
        self.console.print(markdown_content)
        self.console.print()

    def prompt(self) -> str | None:
        for prompt in self:
            return prompt
        exit()

    def ask_single_question(self, query_message: str) -> str:
        answer = self.console.input(f"[bold cyan]{query_message}[/]")
        return answer.strip()
