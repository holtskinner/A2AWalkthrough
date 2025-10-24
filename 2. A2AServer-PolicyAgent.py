import base64
import os
from pathlib import Path

import uvicorn
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from a2a.utils import new_agent_text_message
from anthropic import AnthropicVertex
from anthropic.types import (
    Base64PDFSourceParam,
    DocumentBlockParam,
    MessageParam,
    TextBlockParam,
)
from dotenv import load_dotenv

from helpers import authenticate


# Same Agent from Module 1
class PolicyAgent:

    def __init__(self):
        load_dotenv()
        credentials, project_id = authenticate()
        self.client = AnthropicVertex(
            project_id=project_id,
            region="global",
            access_token=credentials.token,
        )
        with Path("./data/2026AnthemgHIPSBC.pdf").open("rb") as file:
            self.pdf_data = base64.standard_b64encode(file.read()).decode("utf-8")

    def answer_query(self, prompt: str) -> str:
        response = self.client.messages.create(
            model="claude-haiku-4-5@20251001",
            max_tokens=1024,
            system="You are an expert insurance agent designed to assist with coverage queries. Use the provided documents to answer questions about insurance policies. If the information is not available in the documents, respond with 'I don't know'",
            messages=[
                MessageParam(
                    role="user",
                    content=[
                        DocumentBlockParam(
                            type="document",
                            source=Base64PDFSourceParam(
                                type="base64",
                                media_type="application/pdf",
                                data=self.pdf_data,
                            ),
                        ),
                        TextBlockParam(
                            type="text",
                            text=prompt,
                        ),
                    ],
                )
            ],
        )
        return response.content[0].text


class InsuranceAgentExecutor(AgentExecutor):
    """This is an agent for questions around policy coverage, it uses a RAG pattern to find answers based on policy documentation. Use it to help answer questions on coverage and waiting periods."""

    def __init__(self) -> None:
        self.agent = PolicyAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        prompt = context.get_user_input()
        response = self.agent.answer_query(prompt)
        await event_queue.enqueue_event(new_agent_text_message(response))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass


if __name__ == "__main__":
    print("Running Health Insurance Policy Agent")
    load_dotenv()
    PORT = int(os.environ.get("POLICY_AGENT_PORT", 9999))
    HOST = os.environ.get("AGENT_HOST", "localhost")

    skill = AgentSkill(
        id="insurance_coverage",
        name="Insurance coverage",
        description="Provides information about insurance coverage options and details.",
        tags=["insurance", "coverage"],
        examples=["What does my policy cover?", "Are mental health services included?"],
    )

    agent_card = AgentCard(
        name="InsurancePolicyCoverageAgent",
        description="Provides information about insurance policy coverage options and details.",
        url=f"http://{HOST}:{PORT}/",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=False),
        skills=[skill],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=InsuranceAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    uvicorn.run(server.build(), host=HOST, port=PORT)
