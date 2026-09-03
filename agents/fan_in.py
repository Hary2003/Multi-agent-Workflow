from langchain_core.messages import AIMessage
from state import AgentState


def fan_in_node(state: AgentState) -> dict:
    """
    Fan-In Aggregator Node: Collects responses from Research, Planner, and Coder
    subgraphs executing in parallel and synthesizes them into a final combined output.
    """
    user_input = state.get("user_input", "")
    research_analysis = state.get("research_analysis", "N/A")
    research_output = state.get("research_output", "No research output recorded.")
    
    planner_breakdown = state.get("planner_breakdown", "N/A")
    planner_output = state.get("planner_output", "No planner output recorded.")
    
    coder_review = state.get("coder_review", "N/A")
    coder_output = state.get("coder_output", "No coder output recorded.")

    print(f"  [Fan-In Aggregator] Collecting sub-graph outputs for: '{user_input}'")

    synthesis = (
        f"=== FAN-IN SYNTHESIZED REPORT ===\n"
        f"Task Prompt: '{user_input}'\n\n"
        f"1. RESEARCH SUBGRAPH (Research -> Analyze -> Summarize):\n"
        f"   - Intermediate Analysis: {research_analysis}\n"
        f"   - Final Summary:\n{research_output}\n\n"
        f"2. PLANNER SUBGRAPH (Understand -> Break down -> Create plan):\n"
        f"   - Modular Breakdown: {planner_breakdown}\n"
        f"   - Final Plan:\n{planner_output}\n\n"
        f"3. CODER SUBGRAPH (Generate -> Review -> Improve):\n"
        f"   - Code Review: {coder_review}\n"
        f"   - Final Code Output:\n{coder_output}\n"
        f"================================="
    )

    print("  [Fan-In Aggregator] Subgraph outputs successfully aggregated.")

    return {
        "final_response": synthesis,
        "agent_response": synthesis,
        "next_agent": "FINISH",
        "messages": [AIMessage(content=synthesis)],
    }

