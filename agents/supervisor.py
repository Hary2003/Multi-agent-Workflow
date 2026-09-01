from state import AgentState

# Valid routing targets
OPTIONS = ["researcher", "coder", "FINISH"]


def supervisor_node(state: AgentState) -> dict:
    """
    Supervisor node that orchestrates workflow execution.
    It inspects state (user_input and current next_agent state)
    to route execution to worker nodes or signal graph completion ("FINISH").
    """
    user_input = state.get("user_input", "").strip()
    user_input_lower = user_input.lower()
    messages = state.get("messages", [])
    current_next_agent = state.get("next_agent", None)

    print(f"  [Supervisor] State check (Input: '{user_input}', Current next_agent: '{current_next_agent}', History: {len(messages)} msgs)")

    # If a worker agent (researcher or coder) just executed in this turn, complete the workflow turn
    if current_next_agent in ["researcher", "coder"]:
        chosen_agent = "FINISH"
        supervisor_log = f"[Supervisor] Worker node '{current_next_agent}' completed task. Routing workflow to FINISH."
    else:
        # Route based on user input intent
        if "code" in user_input_lower or "script" in user_input_lower or "python" in user_input_lower:
            chosen_agent = "coder"
        elif "research" in user_input_lower or "search" in user_input_lower or "explain" in user_input_lower:
            chosen_agent = "researcher"
        elif "finish" in user_input_lower or "done" in user_input_lower or "exit" in user_input_lower:
            chosen_agent = "FINISH"
        else:
            # Default fallback worker node
            chosen_agent = "researcher"

        supervisor_log = f"[Supervisor] Directed task execution to worker node: '{chosen_agent}'."

    print(f"  [Supervisor] Decision -> Routing to: '{chosen_agent}'")

    return {
        "next_agent": chosen_agent,
        "agent_response": supervisor_log,
    }
