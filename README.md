# Intro to A2A Protocol

## Next Steps

- [X] Switch Models to use Vertex AI/Model Garden
- [X] Change SmolAgents Example to use ADK with Gemini/Google Search?
- [X] Incorporate [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [ ] Incorporate [BeeAI Framework](https://github.com/i-am-bee/beeai-framework)

### Possible Structure

1. Basic Question Answering Agent about Insurance Policies with Gemini or Model as a Service on Vertex AI (No Agent Framework)
    - [ ] Figure out how MaaS APIs would work for DL.AI Cloud Environment
2. [Policy Agent] Turn basic Agent into A2A Agent Server with A2A SDK (No Framework to show how the SDK works.)
3. Basic A2A Client with A2A SDK to show communication (No Framework to show how SDK works)
4. [Research Agent] ADK Agent using Google Search tool with Gemini to answer Health-based Questions. [Using ADK A2A exposing](https://google.github.io/adk-docs/a2a/quickstart-exposing/).
5. [Chained Agent] ADK `WorkflowAgent` connecting to Policy Agent and Health Agent in sequence. Using [ADK A2A consuming](https://google.github.io/adk-docs/a2a/quickstart-consuming/).
6. [Provider Agent] A2AxMCP Agent built with Microsoft Agent Framework and OpenAI OSS
    - Explore Changing this to PydanticAI
7. A2A Client with Microsoft Agent Framework
8. [Health Agent] Full General Healthcare Agent built with [BeeAI Requirements Agent](https://framework.beeai.dev/experimental/requirement-agent) to call all the A2A Agents in an Agentic way.
