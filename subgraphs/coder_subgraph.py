from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage
from state import AgentState


def generate_step(state: AgentState) -> dict:
    """Stage 1: Generate - Write initial draft code implementation."""
    user_input = state.get("user_input", "")
    print(f"    [Coder Subgraph -> 1. Generate] Drafting initial solution for: '{user_input}'")
    draft = f"[Coder Draft] Drafted initial code implementation structure for '{user_input}'."
    return {"coder_draft": draft}


def review_step(state: AgentState) -> dict:
    """Stage 2: Review - Evaluate draft code against quality, security, and performance criteria."""
    user_input = state.get("user_input", "")
    draft = state.get("coder_draft", "")
    print(f"    [Coder Subgraph -> 2. Review] Reviewing draft code for: '{user_input}'")
    review = f"[Coder Review] Passed static code inspection and architectural validation: '{draft}'"
    return {"coder_review": review}


def improve_step(state: AgentState) -> dict:
    """Stage 3: Improve - Refine and produce production-ready code response."""
    user_input = state.get("user_input", "")
    review = state.get("coder_review", "")
    print(f"    [Coder Subgraph -> 3. Improve] Polish and finalize code implementation for: '{user_input}'")
    final_code = (
        f"[Coder Subgraph Output]\n"
        f"• Task: '{user_input}'\n"
        f"• Verification: {review}\n"
        f"• Final Implementation: Production-grade module verified with full unit test coverage and clean interfaces."
    )
    return {
        "coder_output": final_code,
        "messages": [AIMessage(content=final_code)]
    }


def create_coder_subgraph():
    """Builds and compiles the Coder Subgraph pipeline."""
    builder = StateGraph(AgentState)
    builder.add_node("generate", generate_step)
    builder.add_node("review", review_step)
    builder.add_node("improve", improve_step)

    builder.add_edge(START, "generate")
    builder.add_edge("generate", "review")
    builder.add_edge("review", "improve")
    builder.add_edge("improve", END)

    return builder.compile()


coder_subgraph = create_coder_subgraph()
