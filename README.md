# Intro to A2A Protocol

1. Basic Question Answering Agent about Insurance Policies with Claude Model as a Service on Vertex AI (No Agent Framework)
    - [ ] Figure out how MaaS APIs would work for DL.AI Cloud Environment
    - [ ] Add Optional Reading Item to show how to use CrewAI with this.
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

Follow these steps to set up your environment and run the example agents. Each numbered module (`1. ...`, `2. ...`, etc.) is designed to be run in sequence.

#### 1. Initial Setup

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

#### 2. Running the Examples

Agent servers (`2`, `4`, `6`, `8`) are long-running processes. You must open a new terminal for each one and leave it running in the background to proceed with the walkthrough.

**Example 1: Basic Question Answering**

This script runs a single query and then exits.

```sh
# In your terminal:
uv run 1.\ BasicQA.py
```

---

**Examples 2 & 3: Basic A2A Communication**

This demonstrates a basic client-server interaction.

1. **Start the Policy Agent Server:** (Leave this running)

    ```sh
    # In Terminal 1:
    uv run 2.\ A2AServer-PolicyAgent.py
    ```

2. **Run the A2A Client:**

    ```sh
    # In Terminal 2:
    uv run 3.\ A2AClient.py
    ```

    This client will connect to the server from the previous step.

---

**Example 4: Health Research Agent**

Next, we connect the same client to a different agent.

1. **Start the Research Agent Server:** (Leave this running)

    ```sh
    # In Terminal 3:
    uv run 4.\ ADKA2A-ResearchAgent.py
    ```

2. **Update the Client:**
    - Open the file `3. A2AClient.py` in your editor.
    - Comment out the lines for "Module 2" and uncomment the lines for "Module 4" under the `TODO` section to switch the target agent.

3. **Run the A2A Client Again:**

    ```sh
    # In Terminal 2 (or a new one):
    uv run 3.\ A2AClient.py
    ```

    The client will now connect to the research agent.

---

**Example 5: Sequential (Chained) Agent**

This agent connects to the two A2A Agents you already have running.

*Ensure the `Policy Agent` (Module 2) and `Research Agent` (Module 4) are still running in their respective terminals.*

```sh
# In a new terminal:
uv run 5.\ ADKSequentialAgent.py
```

---

**Examples 6 & 7: Provider Agent with LangGraph**

This demonstrates an agent built with LangGraph interacting with a client built with Microsoft Agent Framework.

1. **Start the Provider Agent Server:** (Leave this running)

    ```sh
    # In a new terminal:
    uv run 6.\ A2AxMCPLangGraph-ProviderAgent.py
    ```

2. **Run the Microsoft A2A Client:**

    ```sh
    # In another new terminal:
    uv run 7.\ A2AMicrosoftClient.py
    ```

---

**Examples 8 & 9: General Healthcare Agent with BeeAI**

This showcases a complex agent that orchestrates multiple agents.

1. **Start the General Healthcare Agent Server:** (Leave this running)

    ```sh
    # In a new terminal:
    uv run 8.\ BeeAIRequirementAgent.py
    ```

2. **Run the BeeAI Client:**

    ```sh
    # In another new terminal:
    uv run 9.\ BeeAIClient.py
    ```

    This client starts an interactive chat session with the main healthcare agent.
    Type in a prompt like:

    ```none
    I'm based in Boston, MA. How do I get mental health therapy near me and what does my insurance cover?
    ```
