from langchain_core.messages import AIMessage
from state import AgentState


def optimizer_node(state: AgentState) -> dict:
    """
    Optimizer Node: Formulates targeted optimization directives based on Evaluator feedback.
    Guides Supervisor and Subgraphs on what to refine in the next iteration pass.
    """
    user_input = state.get("user_input", "")
    feedback = state.get("evaluation_feedback", "")
    iteration = state.get("iteration_count", 1)

    print(f"  [Optimizer Node] Formulating optimization plan based on feedback: '{feedback}'")

    directives = (
        f"[Optimizer Directives (Pass {iteration + 1})]\n"
        f"1. Inject production security protocols (JWT, TLS, input sanitization).\n"
        f"2. Add deployment containerization steps (Docker / Kubernetes manifest)."
    )

    log_msg = f"[Optimizer] Formulated refinement directives for iteration {iteration + 1}."
    print(f"  {log_msg}")

    return {
        "optimization_directives": directives,
        "next_agent": "supervisor",
        "messages": [AIMessage(content=log_msg)]
    }
