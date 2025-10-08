import asyncio
import sys
import traceback

from beeai_framework.adapters.a2a.agents import A2AAgent, A2AAgentUpdateEvent
from beeai_framework.emitter import EventMeta
from beeai_framework.errors import FrameworkError
from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.memory.unconstrained_memory import UnconstrainedMemory


async def main() -> None:
    prompt = "I'm based in Boston, MA. How do I get mental health therapy near me and what does my insurance cover?"
    print("ℹ️", "Initializing agents and tools")

    agent = A2AAgent(url="http://localhost:9999", memory=UnconstrainedMemory())

    def print_update(data: A2AAgentUpdateEvent, event: EventMeta) -> None:
        value = data.value
        debug_info = value[1] if isinstance(value, tuple) else value
        print("Agent 🤖 (debug) : ", str(debug_info))

    response = await agent.run(prompt).on("update", print_update)

    print("Agent 🤖 : ", response.last_message.text)

    # destination_expert = RequirementAgent(
    #     name="DestinationExpert",
    #     description="A specialist in local attractions, history, and cultural information",
    #     llm=ChatModel.from_name("ollama:granite3.3:8b"),
    #     memory=UnconstrainedMemory(),
    #     tools=[ThinkTool(), WikipediaTool(), DuckDuckGoSearchTool()],
    #     requirements=[
    #         AskPermissionRequirement(exclude=ThinkTool),
    #         ConditionalRequirement("Wikipedia", min_invocations=1),
    #         ConditionalRequirement(
    #             "DuckDuckGo", only_after="Wikipedia", max_invocations=2
    #         ),
    #     ],
    #     role="Destination Research Specialist",
    #     instructions=(
    #         "You are a knowledgeable travel destination expert with deep expertise in global attractions, "
    #         "cultural insights, and local history. When researching destinations, first establish foundational "
    #         "information through Wikipedia to understand the location's basic context, then use targeted web "
    #         "searches to discover current attractions, seasonal events, and cultural considerations. Always provide "
    #         "travelers with comprehensive information including must-see attractions, cultural customs, local "
    #         "transportation options, and insider tips. Ensure all recommendations are specific to the destination and "
    #         "tailored to create authentic travel experiences."
    #     ),
    # )
    # print("ℹ️", "Destination expert agent initialized")

    # travel_meteorologist = RequirementAgent(
    #     name="TravelMeteorologistPro",
    #     description="An expert on seasonal weather patterns and climate considerations for travelers",
    #     llm=ChatModel.from_name("ollama:granite3.3:8b"),
    #     memory=UnconstrainedMemory(),
    #     tools=[ThinkTool(), OpenMeteoTool()],
    #     requirements=[
    #         ConditionalRequirement(
    #             ThinkTool, force_at_step=1, consecutive_allowed=False
    #         ),
    #         AskPermissionRequirement(
    #             OpenMeteoTool, remember_choices=True, hide_disallowed=False
    #         ),
    #         ConditionalRequirement(OpenMeteoTool, force_at_step=2, min_invocations=1),
    #     ],
    #     role="Travel Weather Specialist",
    #     instructions=(
    #         "You are a travel-focused meteorologist specializing in providing climate insights for travelers. "
    #         "Always assess current and forecasted weather conditions with a travel perspective, highlighting factors "
    #         "that would impact sightseeing, outdoor activities, or transportation. Include specific details about "
    #         "temperature ranges, precipitation likelihood, UV index for sun protection, and appropriate clothing "
    #         "recommendations. Explain seasonal patterns and how they might affect a traveler's experience, including "
    #         "whether current conditions are typical or unusual for the season. Proactively suggest schedule "
    #         "adjustments or alternative activities based on weather forecasts."
    #     ),
    # )
    # print("ℹ️", "Travel meteorologist agent initialized")

    # travel_advisor = RequirementAgent(
    #     name="TravelAdvisor",
    #     description="A personal travel concierge who helps plan perfect trips",
    #     llm=ChatModel.from_name("ollama:granite3.3:8b"),
    #     tools=[
    #         ThinkTool(),
    #         HandoffTool(
    #             destination_expert,
    #             name="DestinationResearch",
    #             description="Consult our Destination Expert for information about attractions, cultural insights, and local travel tips.",
    #         ),
    #         HandoffTool(
    #             travel_meteorologist,
    #             name="WeatherPlanning",
    #             description="Consult our Travel Meteorologist for weather forecasts, seasonal conditions, and climate considerations for your trip.",
    #         ),
    #     ],
    #     requirements=[
    #         ConditionalRequirement(ThinkTool, consecutive_allowed=False),
    #         AskPermissionRequirement(["DestinationResearch", "WeatherPlanning"]),
    #     ],
    #     role="Travel Concierge",
    #     instructions=(
    #         "You are a knowledgeable Travel Advisor who specializes in creating personalized travel experiences. "
    #         "Your goal is to help travelers plan their perfect trips by coordinating information about destinations "
    #         "and weather considerations. For questions about attractions, cultural insights, local customs, or historical "
    #         "information, consult the Destination Expert. For weather forecasts, seasonal patterns, and climate-related "
    #         "travel advice, consult the Travel Meteorologist. Before delegating questions, assess what specific information "
    #         "would benefit the traveler's planning process. When synthesizing information from specialists, create personalized "
    #         "recommendations that consider both destination features and weather conditions."
    #     ),
    #     notes=[
    #         "If user does not provide a valid destination, use 'final_answer' tool for clarification."
    #     ],
    # )

    # print("ℹ️", "Travel advisor agent initialized")
    # print(
    #     "🤖 Travel Advisor:",
    #     "Hi! I'm your personal Travel Advisor, here to help plan your ideal trip.\n"
    #     "I can provide information about destinations, attractions, and local culture, as well as weather forecasts "
    #     "and seasonal considerations.\nHow may I assist with your travel plans today?",
    # )
    # try:
    #     print("✅", "Processing with travel advisor agent")
    #     response = await travel_advisor.run(
    #         prompt,
    #         expected_output="Detailed trip plan for a given destination. Formated as markdown.",
    #     ).middleware(
    #         GlobalTrajectoryMiddleware(excluded=[Requirement])
    #     )  # log tracejtory
    #     print("✅", "Response received from agent")
    #     print("🤖 Travel Advisor:\n", response.last_message.text)
    # except FrameworkError as e:
    #     print("❌ Error:", e.explain())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except FrameworkError as e:
        print("🛑", f"Fatal framework error: {e!s}")
        traceback.print_exc()
        sys.exit(e.explain())
    except KeyboardInterrupt:
        print("ℹ️", "Application terminated by user")
        print("ℹ️", "Exiting chat...")
        sys.exit(0)
