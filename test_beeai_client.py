import asyncio
import os
import sys
import traceback

from beeai_framework.adapters.a2a.agents import A2AAgent, A2AAgentUpdateEvent
from beeai_framework.emitter import EventMeta
from beeai_framework.errors import FrameworkError
from beeai_framework.memory.unconstrained_memory import UnconstrainedMemory
from beeai_framework.utils.models import ModelLike, to_model_optional
from termcolor import colored

from pydantic import BaseModel


class ReaderOptions(BaseModel):
    fallback: str = ""
    input: str = "User 👤 : "
    allow_empty: bool = False


class ConsoleReader:
    def __init__(self, options: ModelLike[ReaderOptions] | None = None) -> None:
        options = to_model_optional(ReaderOptions, options) or ReaderOptions()
        self.fallback = options.fallback
        self.input = options.input
        self.allow_empty = options.allow_empty

    def __iter__(self) -> "ConsoleReader":
        print("Interactive session has started. To escape, input 'q' and submit.")
        return self

    def __next__(self) -> str:
        try:
            while True:
                prompt = input(colored(self.input, "cyan", attrs=["bold"])).strip()
                if not sys.stdin.isatty() and "PYCHARM_HOSTED" not in os.environ:
                    print(prompt)

                if prompt == "q":
                    raise StopIteration

                prompt = prompt if prompt else self.fallback

                if not prompt and not self.allow_empty:
                    print("Error: Empty prompt is not allowed. Please try again.")
                    continue

                return prompt
        except (EOFError, KeyboardInterrupt):
            print()
            exit()

    def write(self, role: str, data: str) -> None:
        print(colored(role, "red", attrs=["bold"]), data)

    def prompt(self) -> str | None:
        for prompt in self:
            return prompt
        exit()

    def ask_single_question(self, query_message: str) -> str:
        answer = input(colored(query_message, "cyan", attrs=["bold"]))
        return answer.strip()


async def main() -> None:
    reader = ConsoleReader()

    agent = A2AAgent(url="http://127.0.0.1:9999", memory=UnconstrainedMemory())
    for prompt in reader:
        # Run the agent and observe events
        def print_update(data: A2AAgentUpdateEvent, event: EventMeta) -> None:
            value = data.value
            debug_info = value[1] if isinstance(value, tuple) else value
            reader.write("Agent 🤖 (debug) : ", str(debug_info))

        response = await agent.run(prompt).on("update", print_update)

        reader.write("Agent 🤖 : ", response.last_message.text)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except FrameworkError as e:
        traceback.print_exc()
        sys.exit(e.explain())
