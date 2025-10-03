from dotenv import load_dotenv
from google.adk.agents import Agent

load_dotenv()
import os

import vertexai
from dotenv import load_dotenv, set_key
from google.adk.agents.llm_agent import LlmAgent
from google.adk.artifacts.in_memory_artifact_service import (
    InMemoryArtifactService,
)  # Optional
from google.adk.models import LlmRequest
from google.adk.planners import BasePlanner, BuiltInPlanner, PlanReActPlanner
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from google.auth import default
from google.genai import types
from google.genai.types import GenerateContentConfig, ThinkingConfig
from vertexai.preview import rag

load_dotenv()

CORPUS_DISPLAY_NAME = "Insurance Documents"
CORPUS_DESCRIPTION = "Corpus containing Insurance Coverage Documents"

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
if not PROJECT_ID:
    raise ValueError(
        "GOOGLE_CLOUD_PROJECT environment variable not set. Please set it in your .env file."
    )
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
if not LOCATION:
    raise ValueError(
        "GOOGLE_CLOUD_LOCATION environment variable not set. Please set it in your .env file."
    )

ENV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".env"))


def set_up_rag_corpus() -> None:
    credentials, _ = default()
    vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=credentials)
    print("Creating RAG Corpus")
    # Create RAG Corpus
    corpus = rag.create_corpus(
        display_name=CORPUS_DISPLAY_NAME,
        description=CORPUS_DESCRIPTION,
    )

    print("RAG Corpus created:", corpus.name)
    # Update the .env file with the corpus name
    set_key(ENV_FILE_PATH, "RAG_CORPUS", corpus.name)

    print("Uploading document to RAG Corpus")
    # Upload the PDF to the corpus
    _ = rag.upload_file(
        corpus_name=corpus.name,
        path="./data/gold-hospital-and-premium-extras.pdf",
        display_name="Gold Hospital and Premium Extras",
        description="Coverage Information for Gold Insurance",
    )


if __name__ == "__main__":

    # Agent Interaction
    def call_agent(query):
        content = types.Content(role="user", parts=[types.Part(text=query)])
        events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

        for event in events:
            print(f"\nDEBUG EVENT: {event}\n")
            if event.is_final_response() and event.content:
                final_answer = event.content.parts[0].text.strip()
                print("\n🟢 FINAL ANSWER\n", final_answer, "\n")

    set_up_rag_corpus()

    ask_vertex_retrieval = VertexAiRagRetrieval(
        name="retrieve_rag_documentation",
        description=(
            "Use this tool to retrieve documentation and reference materials for the question from the RAG corpus,"
        ),
        rag_resources=[rag.RagResource(rag_corpus=os.environ.get("RAG_CORPUS"))],
        similarity_top_k=10,
        vector_distance_threshold=0.6,
    )

    insurance_agent = Agent(
        model="gemini-2.5-flash-lite",
        name="insurance_agent",
        description="An agent that provides information about insurance policy coverage.",
        instruction="""You are an expert insurance agent designed to assist with coverage queries. Use the provided documents to answer questions about insurance policies. If the information is not available in the documents, respond with 'I don't know'""",
        tools=[ask_vertex_retrieval],
    )

    APP_NAME = "weather_app"
    USER_ID = "1234"
    SESSION_ID = "session1234"

    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    runner = Runner(
        agent=insurance_agent, app_name=APP_NAME, session_service=session_service
    )

    call_agent("What is the waiting period for rehabilitation?")
