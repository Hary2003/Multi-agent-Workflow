from state import AgentState

# Valid routing targets
OPTIONS = ["fan_out", "FINISH"]


def supervisor_node(state: AgentState) -> dict:
    """
    Supervisor Node: Orchestrates Fan-Out parallel execution by dispatching tasks
    concurrently to Research, Planner, and Coder worker nodes.
    """
    user_input = state.get("user_input", "").strip()

    print(f"  [Supervisor Fan-Out] Dispatching input to Research, Planner, and Coder in parallel: '{user_input}'")

    supervisor_log = "[Supervisor] Fanned out task execution to Research, Planner, and Coder agents."

    return {
        "next_agent": "fan_out",
        "agent_response": supervisor_log,
    }


