from langchain_core.messages import AIMessage
from state import AgentState


def approval_node(state: AgentState) -> dict:
    """
    Approval Node (Human-in-the-Loop Interrupt):
    Pauses workflow execution after Evaluator deems output GOOD.
    Waits for explicit human review and approval or feedback.
    """
    is_approved = state.get("is_approved", False)
    approval_status = state.get("approval_status", "")
    feedback = state.get("approval_feedback", "")
    final_response = state.get("final_response", "")

    if is_approved or approval_status == "approved":
        log_msg = f"[Approval Node] Task APPROVED by human reviewer. Feedback: '{feedback or 'None'}'"
        print(f"  {log_msg}")
        return {
            "approval_status": "approved",
            "is_approved": True,
            "agent_response": f"Approved output. {final_response}",
            "next_agent": "FINISH",
            "messages": [AIMessage(content=log_msg)]
        }
    elif approval_status == "rejected":
        log_msg = f"[Approval Node] Task REJECTED by human reviewer. Feedback: '{feedback}'"
        print(f"  {log_msg}")
        return {
            "approval_status": "rejected",
            "is_approved": False,
            "agent_response": f"Rejected by user: {feedback}",
            "next_agent": "optimizer",
            "messages": [AIMessage(content=log_msg)]
        }
    else:
        # Default entry: Pending human review interrupt
        log_msg = "[Approval Node] [INTERRUPT]: Awaiting explicit human approval/review."
        print(f"  {log_msg}")
        return {
            "approval_status": "pending",
            "is_approved": False,
            "agent_response": log_msg,
            "next_agent": "approval_node",
            "messages": [AIMessage(content=log_msg)]
        }
