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
from smolagents import (
    CodeAgent,
    DuckDuckGoSearchTool,
    LiteLLMModel,
    VisitWebpageTool,
)


class HealthAgentExecutor(AgentExecutor):
    """This is a CodeAgent which supports the hospital to handle health based questions for patients. Current or prospective patients can use it to find answers about their health and hospital treatments."""

    def __init__(self):
        load_dotenv()

        model = LiteLLMModel(
            model_id="gemini/gemini-2.5-pro",
            num_ctx=8192,
        )
        self.agent = CodeAgent(
            tools=[DuckDuckGoSearchTool(), VisitWebpageTool()], model=model
        )

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        response = self.agent.run(context.get_user_input())
        await event_queue.enqueue_event(new_agent_text_message(str(response)))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass


if __name__ == "__main__":
    PORT = 9998
    HOST = "0.0.0.0"

    skill = AgentSkill(
        id="general_health_inquiry",
        name="General Health Information",
        description="Provides information about symptoms, health conditions, treatments, and procedures using up-to-date web resources.",
        tags=["health", "treatment", "symptoms", "hospital"],
        examples=[
            "What are the common symptoms of influenza?",
            "Tell me about the recovery time for a meniscus tear.",
            "What is the latest treatment for severe allergies?",
        ],
    )

    agent_card = AgentCard(
        name="Hospital Health Agent",
        description="Supports the hospital to handle health based questions for patients. Current or prospective patients can use it to find answers about their health and hospital treatments.",
        url=f"http://{HOST}:{PORT}/",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=HealthAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    uvicorn.run(server.build(), host=HOST, port=PORT)
