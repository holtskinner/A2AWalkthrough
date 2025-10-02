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
from dotenv import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig, Part


class InsuranceAgentExecutor(AgentExecutor):
    """This is an agent for questions around policy coverage, it uses a RAG pattern to find answers based on policy documentation. Use it to help answer questions on coverage and waiting periods."""

    def __init__(self):
        load_dotenv()
        self.client = genai.Client()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        with open("./data/2026AnthemgHIPSBC.pdf", "rb") as file:
            pdf_bytes = file.read()

        response = self.client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=[
                Part.from_bytes(
                    data=pdf_bytes,
                    mime_type="application/pdf",
                ),
                context.get_user_input(),
            ],
            config=GenerateContentConfig(
                system_instruction="You are an expert insurance agent designed to assist with coverage queries. Use the provided documents to answer questions about insurance policies. Provide detailed answers in your responses. If the information is not available in the documents, respond with 'I don't know'",
            ),
        )
        await event_queue.enqueue_event(new_agent_text_message(response.text))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass


if __name__ == "__main__":
    PORT = 9999
    HOST = "0.0.0.0"

    skill = AgentSkill(
        id="insurance_coverage",
        name="Insurance coverage",
        description="Provides information about insurance coverage options and details.",
        tags=["insurance", "coverage"],
        examples=["What does my policy cover?", "Are mental health services included?"],
    )

    agent_card = AgentCard(
        name="Insurance Coverage Agent",
        description="Provides information about insurance coverage options and details.",
        url=f"http://{HOST}:{PORT}/",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
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
