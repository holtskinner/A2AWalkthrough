# Intro to A2A Protocol

1. Conceptual Content - No Code Samples
2. Basic Question Answering Agent about Insurance Policies with Claude Model as a Service on Vertex AI (No Agent Framework)
3. [Insurance Policy Agent] Turn QA Agent into A2A Agent Server with A2A SDK (No Framework to show how the SDK works.)
4. Basic A2A Client with A2A SDK to show communication (No Framework to show how SDK works)
5. [Health Research Agent] ADK Agent using Gemini with Google Search tool to answer Health-based Questions. Using [ADK A2A exposing](https://google.github.io/adk-docs/a2a/quickstart-exposing/).
6. [Sequential Agent] ADK `SequentialAgent` connecting to Policy Agent and Health Agent in sequence. Using [ADK A2A consuming](https://google.github.io/adk-docs/a2a/quickstart-consuming/).
7. [Healthcare Provider Agent] A2A Agent calling an MCP Server, built with LangGraph and OpenAI OSS on Vertex AI.
    - [Built-in LangGraph support](https://docs.langchain.com/langsmith/server-a2a) seems to require using LangGraph platform/dev server, which might not work for this example.
8. A2A Client with [Microsoft Agent Framework built-in Client](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-types/a2a-agent?pivots=programming-language-python)
9. [Healthcare Concierge Agent] Full General Healthcare Agent built with [BeeAI Requirements Agent](https://framework.beeai.dev/experimental/requirement-agent) to call all of the A2A Agents in an Agentic way.
    - Using [BeeAI Built-in A2A Support](https://framework.beeai.dev/integrations/a2a)

## How to Run

Follow these steps to set up your environment and run the example agents. Each numbered module (`1. ...`, `2. ...`, etc.) is designed to be run in sequence.

### 1. Initial Setup

Before running the examples, complete the following setup steps:

1. **Authenticate with Google Cloud:**
    - Create or select a Google Cloud Project.
    - Enable the Vertex AI API in your project.
    - Enable the Model Garden models used in the modules
      - [Claude 4.5 Haiku](https://console.cloud.google.com/vertex-ai/publishers/anthropic/model-garden/claude-haiku-4-5)
      - [GPT OSS 120b](https://console.cloud.google.com/vertex-ai/publishers/openai/model-garden/gpt-oss-120b-maas)
    - Set up your local application-default credentials by running `gcloud auth application-default login`.

2. **Configure Environment Variables:**
    - In the project root, make a copy of `example.env` and rename it to `.env`.

    ```sh
    cp example.env .env
    ```
