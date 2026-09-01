from langchain_core.messages import AIMessage
from state import AgentState


def researcher_node(state: AgentState) -> dict:
    """
    Researcher Worker Node: Performs research tasks and responds back to the supervisor.
    """
    user_input = state.get("user_input", "")
    print(f"  [Researcher Worker] Executing research logic for input: '{user_input}'")

    response = f"[Researcher] Completed research analysis for topic: '{user_input}'."
    
    return {
        "agent_response": response,
        "messages": [AIMessage(content=response)],
    }


def coder_node(state: AgentState) -> dict:
    """
    Coder Worker Node: Writes code or performs software engineering tasks and responds back to the supervisor.
    """
    user_input = state.get("user_input", "")
    print(f"  [Coder Worker] Executing code generation logic for input: '{user_input}'")

    response = f"[Coder] Generated solution implementation for task: '{user_input}'."

    return {
        "agent_response": response,
        "messages": [AIMessage(content=response)],
    }
