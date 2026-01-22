# Intro to A2A Protocol

1. Basic Question Answering Agent about Insurance Policies with No Agent Framework
2. [Insurance Policy Agent] Turn QA Agent into A2A Agent Server with A2A SDK (No Framework to show how the SDK works.)
3. Basic A2A Client with A2A SDK to show communication (No Framework to show how SDK works)
4. [Health Research Agent] ADK Agent using Gemini with Google Search tool to answer Health-based Questions. Using [ADK A2A exposing](https://google.github.io/adk-docs/a2a/quickstart-exposing/).
5. [Sequential Agent] ADK `SequentialAgent` connecting to Policy Agent and Health Agent in sequence. Using [ADK A2A consuming](https://google.github.io/adk-docs/a2a/quickstart-consuming/).
6. [Healthcare Provider Agent] A2A Agent calling an MCP Server, built with LangChain/LangGraph.
    - Uses [`langgraph-a2a-server`](https://github.com/5enxia/langgraph-a2a-server)
7. A2A Client with [Microsoft Agent Framework built-in Client](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-types/a2a-agent?pivots=programming-language-python)
8. [Healthcare Concierge Agent] Full General Healthcare Agent built with [BeeAI Requirements Agent](https://framework.beeai.dev/experimental/requirement-agent) to call all of the A2A Agents in an Agentic way.
    - Using [BeeAI Built-in A2A Support](https://framework.beeai.dev/integrations/a2a)

## How to Run

Follow these steps to set up your environment and run the example agents. Each numbered module (`1. ...`, `2. ...`, etc.) is designed to be run in sequence.

### 1. Initial Setup

This project uses `uv` to manage dependencies and Python versions automatically. This ensures that you have the correct Python version (3.12+) and all required libraries without affecting your system Python.

1.  **Install `uv`** (if you haven't already):
    - **macOS/Linux:**

      ```sh
      curl -LsSf https://astral.sh/uv/install.sh | sh
      ```

    - **Windows:**

      ```powershell
      powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
      ```

2.  **Sync the Project:**
    - Run this command in the project root to install the correct Python version and libraries into a local virtual environment (`.venv`):

      ```sh
      uv sync
      ```

3.  **Configure Environment Variables:**
    - In the project root, make a copy of `example.env` and rename it to `.env`.

    ```sh
    cp example.env .env
    ```
    - Replace `"YOUR_GEMINI_API_KEY"` with your actual [Gemini API Key](https://aistudio.google.com/app/api-keys).

4.  **Launch the Notebooks:**
    - To ensure the notebooks use the `uv` environment, launch your editor or Jupyter through `uv run`:

      ```sh
      # For VS Code
      uv run code .

      # For Jupyter Lab
      uv run jupyter lab
      ```

## Running the Agents

You can run the agent servers using `uv run`. Ensure you are in the project root.

- **Policy Agent (Lesson 2):**

  ```sh
  uv run agents/a2a_policy_agent.py
  ```

- **Research Agent (Lesson 4):**

  ```sh
  uv run agents/a2a_research_agent.py
  ```

- **Provider Agent (Lesson 6):**

  ```sh
  uv run agents/a2a_provider_agent.py
  ```

- **Healthcare Concierge Agent (Lesson 8):**

  ```sh
  uv run agents/a2a_healthcare_agent.py
  ```
