from state import AgentState

# Valid routing targets
OPTIONS = ["fan_out", "FINISH"]


def supervisor_node(state: AgentState) -> dict:
    """
    Supervisor Node: Orchestrates Fan-Out parallel execution by dispatching tasks
    concurrently to Research, Planner, and Coder subgraphs.
    """
    user_input = state.get("user_input", "").strip()
    optimization = state.get("optimization_directives", "")

    if optimization:
        print(f"  [Supervisor Fan-Out] Re-dispatching task with Optimization Directives: '{user_input}'")
        supervisor_log = f"[Supervisor] Fanned out task re-execution with directives: {optimization}"
    else:
        print(f"  [Supervisor Fan-Out] Dispatching initial task input: '{user_input}'")
        supervisor_log = "[Supervisor] Fanned out initial task execution to Research, Planner, and Coder subgraphs."

    return {
        "next_agent": "fan_out",
        "agent_response": supervisor_log,
    }



