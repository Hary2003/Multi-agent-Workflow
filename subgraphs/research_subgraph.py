from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage
from state import AgentState


def research_step(state: AgentState) -> dict:
    """Stage 1: Research - Conduct initial context and domain research."""
    user_input = state.get("user_input", "")
    print(f"    [Research Subgraph -> 1. Research] Gathering domain knowledge for: '{user_input}'")
    raw_research = f"[Research Raw] Context, domain concepts, and technical references gathered for '{user_input}'."
    return {"research_raw": raw_research}


def analyze_step(state: AgentState) -> dict:
    """Stage 2: Analyze - Evaluate gathered findings and architectural patterns."""
    user_input = state.get("user_input", "")
    raw = state.get("research_raw", "")
    print(f"    [Research Subgraph -> 2. Analyze] Analyzing findings for: '{user_input}'")
    analysis = f"[Research Analysis] Evaluated requirements & trade-offs based on: '{raw}'"
    return {"research_analysis": analysis}


def summarize_step(state: AgentState) -> dict:
    """Stage 3: Summarize - Produce structured research summary."""
    user_input = state.get("user_input", "")
    analysis = state.get("research_analysis", "")
    print(f"    [Research Subgraph -> 3. Summarize] Synthesizing final research report for: '{user_input}'")
    summary = (
        f"[Research Subgraph Output]\n"
        f"• Task: '{user_input}'\n"
        f"• Analysis Summary: {analysis}\n"
        f"• Key Findings: Comprehensive domain research and system requirement patterns established."
    )
    return {
        "research_output": summary,
        "messages": [AIMessage(content=summary)]
    }


def create_research_subgraph():
    """Builds and compiles the Research Subgraph pipeline."""
    builder = StateGraph(AgentState)
    builder.add_node("research", research_step)
    builder.add_node("analyze", analyze_step)
    builder.add_node("summarize", summarize_step)

    builder.add_edge(START, "research")
    builder.add_edge("research", "analyze")
    builder.add_edge("analyze", "summarize")
    builder.add_edge("summarize", END)

    return builder.compile()


research_subgraph = create_research_subgraph()
