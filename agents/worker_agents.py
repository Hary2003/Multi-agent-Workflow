from langchain_core.messages import AIMessage
from state import AgentState


def researcher_node(state: AgentState) -> dict:
    """
    Researcher Worker Node: Performs research tasks.
    """
    user_input = state.get("user_input", "")
    print(f"  [Researcher Worker] Executing research logic for input: '{user_input}'")

    response = f"[Researcher] Completed comprehensive research on: '{user_input}'."
    
    return {
        "research_output": response,
        "messages": [AIMessage(content=response)],
    }


def coder_node(state: AgentState) -> dict:
    """
    Coder Worker Node: Writes code or performs software engineering tasks.
    """
    user_input = state.get("user_input", "")
    print(f"  [Coder Worker] Executing code generation logic for input: '{user_input}'")

    response = f"[Coder] Generated production-ready implementation for task: '{user_input}'."

    return {
        "coder_output": response,
        "messages": [AIMessage(content=response)],
    }


def planner_node(state: AgentState) -> dict:
    """
    Planner Worker Node: Formulates plans, architecture, and step-by-step strategies.
    """
    user_input = state.get("user_input", "")
    print(f"  [Planner Worker] Executing planning logic for input: '{user_input}'")

    response = f"[Planner] Formulated detailed architecture and step-by-step roadmap for: '{user_input}'."

    return {
        "planner_output": response,
        "messages": [AIMessage(content=response)],
    }



