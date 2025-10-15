# Intro to A2A Protocol

1. Basic Question Answering Agent about Insurance Policies with Claude Model as a Service on Vertex AI (No Agent Framework)
    - [ ] Figure out how MaaS APIs would work for DL.AI Cloud Environment
2. [Policy Agent] Turn QA Agent into A2A Agent Server with A2A SDK (No Framework to show how the SDK works.)
3. Basic A2A Client with A2A SDK to show communication (No Framework to show how SDK works)
4. [Research Agent] ADK Agent using Gemini with Google Search tool to answer Health-based Questions. Using [ADK A2A exposing](https://google.github.io/adk-docs/a2a/quickstart-exposing/).
5. [Chained Agent] ADK `WorkflowAgent` connecting to Policy Agent and Health Agent in sequence. Using [ADK A2A consuming](https://google.github.io/adk-docs/a2a/quickstart-consuming/).
6. [Provider Agent] A2A Agent calling an MCP Server, built with Microsoft Agent Framework and OpenAI OSS on Vertex AI
    - Note: Microsoft Agent Framework doesn't have built in A2A Exposing, need to build `AgentExecutor`.
7. A2A Client with [Microsoft Agent Framework built-in Client](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-types/a2a-agent?pivots=programming-language-python)
8. [Health Agent] Full General Healthcare Agent built with [BeeAI Requirements Agent](https://framework.beeai.dev/experimental/requirement-agent) to call all of the A2A Agents in an Agentic way.
    - Using [BeeAI Built-in A2A Support](https://framework.beeai.dev/integrations/a2a)
