# Intro to A2A Protocol

1. Basic Question Answering Agent about Insurance Policies with Claude Model as a Service on Vertex AI (No Agent Framework)
    - [ ] Figure out how MaaS APIs would work for DL.AI Cloud Environment
2. [Insurance Policy Agent] Turn QA Agent into A2A Agent Server with A2A SDK (No Framework to show how the SDK works.)
3. Basic A2A Client with A2A SDK to show communication (No Framework to show how SDK works)
4. [Health Research Agent] ADK Agent using Gemini with Google Search tool to answer Health-based Questions. Using [ADK A2A exposing](https://google.github.io/adk-docs/a2a/quickstart-exposing/).
5. [Chained Agent] ADK `WorkflowAgent` connecting to Policy Agent and Health Agent in sequence. Using [ADK A2A consuming](https://google.github.io/adk-docs/a2a/quickstart-consuming/).
6. [Healthcare Provider Agent] A2A Agent calling an MCP Server, built with LangGraph and OpenAI OSS on Vertex AI.
    - [Built-in LangGraph support](https://docs.langchain.com/langsmith/server-a2a) seems to require using LangGraph platform/dev server, which might not work for this example.
7. A2A Client with [Microsoft Agent Framework built-in Client](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-types/a2a-agent?pivots=programming-language-python)
8. [General Health Agent] Full General Healthcare Agent built with [BeeAI Requirements Agent](https://framework.beeai.dev/experimental/requirement-agent) to call all of the A2A Agents in an Agentic way.
    - Using [BeeAI Built-in A2A Support](https://framework.beeai.dev/integrations/a2a)

## How to Run

For each module, run:

```sh
uv run filename.py
```

E.g.

```sh
uv run 1.\ BasicQA.py
```

### Procedure for course

- Setup Authentication for Vertex AI
  - Create Google Cloud Project
  - Enable Vertex AI API
  - Enable Vertex AI Model Garden Models
  - Download `credentials.json` file and enable environment.
- Copy `example.env` into `.env`
  - Update `.env` with Google Cloud Project ID
- Run Module 1
- Open a new terminal and Run Module 2. Keep it running
- Open a new terminal and run Module 3
  - This will connect the A2A Client in Module 3 to the A2A Server in Module 2
- Open a new terminal and run Module 4. Keep it running
- Edit Module 3 source code where `TODO` is marked to connect to module 4
- In a new terminal (or the same where you previously ran Module 3) run Module 3
  - This will connect the A2A Client in Module 3 to the A2A Server in Module 4
- Open a new terminal and run Module 5.
  - This will connect to both Module 2 and Module 4
- Open a new terminal and run Module 6. Keep it Running
- Open a new terminal and run Module 7.
  - This will connect the A2A Client in Module 7 to the A2A Server in Module 6.
- Open a new terminal and run Module 8. Keep it running
- Open a new terminal and run Module 9.
  - This will connect the A2A Client in Module 9 to the A2A Server in Module 8.
