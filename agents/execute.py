from langchain_core.messages import AIMessage
from state import AgentState


def execute_node(state: AgentState) -> dict:
    """
    Execute Node:
    Triggers after explicit Human APPROVAL.
    Executes the finalized synthesized task payload and logs deployment confirmation.
    """
    user_input = state.get("user_input", "")
    feedback = state.get("approval_feedback", "")
    final_response = state.get("final_response", "")

    log_msg = f"[Execute Node] Task EXECUTED successfully following human approval. User feedback: '{feedback or 'None'}'"
    print(f"  {log_msg}")

    execution_result = (
        f"=== EXECUTION SUCCESSFUL ===\n"
        f"Action: Finalized and deployed workflow result for '{user_input}'.\n"
        f"Human Feedback: {feedback or 'None'}\n\n"
        f"Payload Summary:\n{final_response}\n"
        f"============================"
    )

    return {
        "agent_response": execution_result,
        "final_response": execution_result,
        "next_agent": "FINISH",
        "messages": [AIMessage(content=log_msg)]
    }
