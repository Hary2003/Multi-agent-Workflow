from langchain_core.messages import AIMessage
from state import AgentState


def fan_in_node(state: AgentState) -> dict:
    """
    Fan-In Aggregator Node: Collects responses from Research, Planner, and Coder
    nodes executing in parallel and synthesizes them into a final combined output.
    """
    user_input = state.get("user_input", "")
    research_output = state.get("research_output", "No research output recorded.")
    planner_output = state.get("planner_output", "No planner output recorded.")
    coder_output = state.get("coder_output", "No coder output recorded.")

    print(f"  [Fan-In Aggregator] Collecting parallel outputs for: '{user_input}'")

    synthesis = (
        f"=== FAN-IN SYNTHESIZED REPORT ===\n"
        f"Task Prompt: '{user_input}'\n\n"
        f"1. RESEARCH RESULTS:\n   {research_output}\n\n"
        f"2. EXECUTION PLAN:\n   {planner_output}\n\n"
        f"3. CODE IMPLEMENTATION:\n   {coder_output}\n"
        f"================================="
    )

    print("  [Fan-In Aggregator] Synthesis complete.")

    return {
        "final_response": synthesis,
        "agent_response": synthesis,
        "next_agent": "FINISH",
        "messages": [AIMessage(content=synthesis)],
    }
